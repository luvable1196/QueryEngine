from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from fastapi import HTTPException, status
from datetime import datetime
from contextlib import asynccontextmanager
import logging
import time
from typing import Dict, Any
import uvicorn

from .routes import query, companies
from .services.database_service import DatabaseService
from .services.nlp_service import NLPService
from .services.cache_service import CompanyDataCacheManager
from .models.response_models import HealthResponse, ErrorResponse, DatabaseStatsResponse, SystemStatsResponse
from .utils.helpers import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

database_service = None
nlp_service = None
cache_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LeetCode Query API...")
    try:
        global database_service, nlp_service, cache_service
        
        # Initialize database service
        database_service = DatabaseService()
        await database_service.initialize()
        
        # Initialize NLP service
        nlp_service = NLPService()
        await nlp_service.initialize()
        
        # Initialize cache service - use the one from database service if available
        try:
            if hasattr(database_service, 'cache_manager') and database_service.cache_manager:
                cache_service = database_service.cache_manager
                logger.info("Using cache manager from database service")
            else:
                logger.info("Database service doesn't have cache manager, cache will be disabled")
                cache_service = None
        except Exception as e:
            logger.warning(f"CacheService initialization failed: {e}. Proceeding without cache.")
            cache_service = None
        
        # Load data if database is empty
        stats = await database_service.get_stats()
        if stats.get('total_problems', 0) == 0:
            logger.info("Database is empty, loading data from files...")
            await database_service.load_data_from_files()
            
        logger.info("LeetCode Query API started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    yield
    logger.info("Shutting down LeetCode Query API...")
    try:
        if database_service:
            await database_service.close()
        if nlp_service:
            await nlp_service.close()
        if cache_service:
            await cache_service.close()
        logger.info("LeetCode Query API shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

app = FastAPI(
    title="LeetCode Query API",
    description="Natural Language Query System for LeetCode Problems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="ValidationError",
            message="Request validation failed",
            details=exc.errors()
        ).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPException",
            message=str(exc.detail)
        ).model_dump()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": str(exc.detail)
        }
    )

def get_database_service() -> DatabaseService:
    if database_service is None:
        raise HTTPException(status_code=503, detail="Database service not initialized")
    return database_service

def get_nlp_service() -> NLPService:
    if nlp_service is None:
        raise HTTPException(status_code=503, detail="NLP service not initialized")
    return nlp_service

def get_cache_service() -> CompanyDataCacheManager:
    if cache_service is None:
        logger.warning("Cache service not initialized, proceeding without cache")
        return None
    return cache_service

app.include_router(
    query.router,
    prefix="/api/v1/query",
    tags=["Query"],
    dependencies=[Depends(get_database_service), Depends(get_nlp_service), Depends(get_cache_service)]
)

app.include_router(
    companies.router,
    prefix="/api/v1/companies",
    tags=["Companies"],
    dependencies=[Depends(get_database_service)]
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        # Health check for cache service
        if cache_service:
            cache_health = await cache_service.health_check()
            if cache_health["status"] != "healthy":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "status": "unhealthy",
                        "service": "cache",
                        "details": cache_health,
                        "timestamp": datetime.now()
                    }
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "unhealthy",
                    "service": "cache",
                    "details": {"status": "unhealthy", "error": "cache_service not available"},
                    "timestamp": datetime.now()
                }
            )

        # Health check for database service
        if database_service:
            db_health = await database_service.health_check()
            if db_health["status"] != "healthy":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "status": "unhealthy",
                        "service": "database",
                        "details": db_health,
                        "timestamp": datetime.now()
                    }
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "unhealthy",
                    "service": "database",
                    "details": {"status": "unhealthy", "error": "database_service not available"},
                    "timestamp": datetime.now()
                }
            )
        stats = await database_service.get_stats() if database_service else {}
        return HealthResponse(
            status="healthy" if db_health["status"] == "healthy" else "unhealthy",
            message="LeetCode Query API is running",
            database_connected=db_health.get("database_connected", False),
            cache_connected=cache_health.get("status") == "healthy",
            total_problems=stats.get("total_problems", 0)
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            message=f"Health check failed: {str(e)}",
            database_connected=False,
            cache_connected=False,
            total_problems=0
        )

@app.get("/health/detailed")
async def detailed_health_check():
    try:
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {}
        }
        if database_service:
            db_health = await database_service.health_check()
            health_data["services"]["database"] = db_health
        else:
            health_data["services"]["database"] = {"status": "not_initialized"}
        if nlp_service:
            nlp_health = await nlp_service.health_check()
            health_data["services"]["nlp"] = nlp_health
        else:
            health_data["services"]["nlp"] = {"status": "not_initialized"}
        if cache_service:
            cache_health = await cache_service.health_check()
            health_data["services"]["cache"] = cache_health
        else:
            health_data["services"]["cache"] = {"status": "not_initialized"}
        unhealthy_services = [
            service for service, status in health_data["services"].items()
            if status.get("status") != "healthy"
        ]
        if unhealthy_services:
            health_data["status"] = "degraded"
            health_data["unhealthy_services"] = unhealthy_services
        return health_data
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

@app.get("/stats/database", response_model=DatabaseStatsResponse)
async def get_database_stats(db_service: DatabaseService = Depends(get_database_service)):
    try:
        stats = await db_service.get_stats()
        return DatabaseStatsResponse(
            total_problems=stats.get("total_problems", 0),
            problems_by_difficulty=stats.get("problems_by_difficulty", {}),
            total_companies=stats.get("total_companies", 0),
            total_topics=stats.get("total_topics", 0),
            average_frequency=stats.get("average_frequency", 0.0),
            average_acceptance_rate=stats.get("average_acceptance_rate", 0.0),
            last_updated=stats.get("last_updated", "Unknown")
        )
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve database statistics")

@app.get("/stats/system", response_model=SystemStatsResponse)
async def get_system_stats(
    db_service: DatabaseService = Depends(get_database_service),
    cache_service: CompanyDataCacheManager = Depends(get_cache_service)
):
    try:
        db_stats = await db_service.get_stats()
        database_stats = DatabaseStatsResponse(
            total_problems=db_stats.get("total_problems", 0),
            problems_by_difficulty=db_stats.get("problems_by_difficulty", {}),
            total_companies=db_stats.get("total_companies", 0),
            total_topics=db_stats.get("total_topics", 0),
            average_frequency=db_stats.get("average_frequency", 0.0),
            average_acceptance_rate=db_stats.get("average_acceptance_rate", 0.0),
            last_updated=db_stats.get("last_updated", "Unknown")
        )
        cache_stats = await cache_service.get_stats() if cache_service else {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "hit_rate": 0.0,
            "cache_size": 0
        }
        return SystemStatsResponse(
            database_stats=database_stats,
            cache_stats=cache_stats,
            uptime="Unknown",
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system statistics")

@app.get("/")
async def root():
    return {
        "message": "LeetCode Query API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/info")
async def api_info():
    return {
        "name": "LeetCode Query API",
        "version": "1.0.0",
        "description": "Natural Language Query System for LeetCode Problems",
        "endpoints": {
            "health": "/health",
            "query": "/api/v1/query/",
            "companies": "/api/v1/companies/",
            "stats": "/stats/",
            "docs": "/docs"
        },
        "features": [
            "Natural language query processing",
            "Advanced filtering and sorting",
            "Company and topic statistics",
            "Caching for improved performance",
            "Comprehensive API documentation"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
  



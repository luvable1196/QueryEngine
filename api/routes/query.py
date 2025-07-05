from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging
import time
from datetime import datetime

from ..services.database_service import DatabaseService
from ..services.nlp_service import NLPService
from ..services.cache_service import CompanyDataCacheManager
from ..models.request_models import (
    QueryRequest, 
    FilterRequest, 
    BulkQueryRequest,
    SortBy,
    SortOrder,
    DifficultyLevel
)
from ..models.response_models import (
    QueryResponse, 
    FilteredQueryResponse,
    BulkQueryResponse,
    SuggestionResponse,
    AutocompleteResponse,
    ProblemResult,
    ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

def get_database_service() -> DatabaseService:
    """Dependency to get database service"""
    from ..main import database_service
    if database_service is None:
        raise HTTPException(status_code=503, detail="Database service not available")
    return database_service

def get_nlp_service() -> NLPService:
    """Dependency to get NLP service"""
    from ..main import nlp_service
    if nlp_service is None:
        raise HTTPException(status_code=503, detail="NLP service not available")
    return nlp_service

def get_cache_service() -> 'DatabaseService':
    """Dependency to get cache service"""
    from ..main import database_service
    if database_service is None:
        logger.error("Cache service not available - service not initialized")
        raise HTTPException(status_code=503, detail="Cache service not available")
    
    # Check cache database status
    try:
        if hasattr(database_service, 'cache_manager') and database_service.cache_manager:
            # Check if cache manager is initialized and connected
            if hasattr(database_service.cache_manager, 'redis_client') and database_service.cache_manager.redis_client:
                logger.debug("Cache database connection verified")
            else:
                logger.warning("Cache database connection not available")
        else:
            logger.warning("Cache manager not initialized")
    except Exception as e:
        logger.error(f"Error checking cache database status: {e}")
    
    return database_service

@router.post("/", response_model=QueryResponse)
async def process_natural_language_query(
    request: QueryRequest,
    db_service: DatabaseService = Depends(get_database_service),
    nlp_service: NLPService = Depends(get_nlp_service),
):
    """
    Process natural language query and return matching problems
    
    Examples:
    - "Give me easy array questions asked by Google"
    - "Show me hard dynamic programming problems"
    - "Find medium tree problems with high frequency"
    """
    try:
        start_time = time.time()
        
        # Parse natural language query
        parsed_intent = await nlp_service.parse_query(request.query)
        logger.info(f"Parsed intent: {parsed_intent}")
        
        # Check cache first using the smart cache manager
        cache_key_params = {
            "type": "nlp_query",
            "query": request.query,
            "parsed_intent": parsed_intent
        }
        
        cached_result = None
        if request.use_cache:
            try:
                cached_result = await db_service.cache_manager.get_cached_query(cache_key_params)
                if cached_result:
                    logger.info(f"Cache hit for query: {request.query}")
                    # Convert cached result back to proper format
                    response_data = {
                        "query": request.query,
                        "parsed_intent": parsed_intent,
                        "results": cached_result.get("results", []),
                        "total_results": cached_result.get("total_results", 0),
                        "execution_time": cached_result.get("execution_time", 0),
                        "cached": True,
                        "pagination": cached_result.get("pagination", {
                            "limit": parsed_intent.get("limit", 50),
                            "offset": parsed_intent.get("offset", 0),
                            "total": cached_result.get("total_results", 0)
                        })
                    }
                    return QueryResponse(**response_data)
            except Exception as cache_error:
                logger.warning(f"Cache retrieval failed: {cache_error}")
        
        # Execute query
        results = await db_service.execute_query(parsed_intent)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Prepare response
        response = QueryResponse(
            query=request.query,
            parsed_intent=parsed_intent,
            results=results,
            total_results=len(results),
            execution_time=execution_time,
            cached=False,
            pagination={
                "limit": parsed_intent.get("limit", 50),
                "offset": parsed_intent.get("offset", 0),
                "total": len(results)
            }
        )
        
        # Cache result using the smart cache manager
        if request.use_cache:
            try:
                cache_data = {
                    "results": [result.dict() if hasattr(result, 'dict') else result for result in results],
                    "total_results": len(results),
                    "execution_time": execution_time,
                    "pagination": {
                        "limit": parsed_intent.get("limit", 50),
                        "offset": parsed_intent.get("offset", 0),
                        "total": len(results)
                    }
                }
                await db_service.cache_manager.cache_query_result(cache_key_params, cache_data)
                logger.info(f"Cached query result for: {request.query}")
            except Exception as cache_error:
                logger.warning(f"Cache storage failed: {cache_error}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query '{request.query}': {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
    

@router.post("/filter", response_model=FilteredQueryResponse)
async def filter_problems(
    request: FilterRequest,
    db_service: DatabaseService = Depends(get_database_service),
    cache_service: CompanyDataCacheManager = Depends(get_cache_service)
):
    """
    Filter problems using structured parameters
    
    Provides advanced filtering capabilities with precise control over:
    - Difficulty levels
    - Topics and companies
    - Frequency and acceptance rate ranges
    - Sorting and pagination
    """
    try:
        start_time = time.time()
        
        # Convert FilterRequest to query parameters
        query_params = {
            "difficulty": request.difficulty,
            "topics": request.topics,
            "companies": request.companies,
            "min_frequency": request.min_frequency,
            "max_frequency": request.max_frequency,
            "min_acceptance_rate": request.min_acceptance_rate,
            "max_acceptance_rate": request.max_acceptance_rate,
            "question_numbers": request.question_numbers,
            "sort_by": request.sort_by,
            "sort_order": request.sort_order,
            "limit": request.limit,
            "offset": request.offset
        }
        
        # Remove None values
        query_params = {k: v for k, v in query_params.items() if v is not None}
        
        # Check cache
        cache_key = f"filter:{hash(str(sorted(query_params.items())))}"
        cached_result = await cache_service.get(cache_key)
        if cached_result:
            logger.info("Cache hit for filter query")
            return FilteredQueryResponse(**cached_result)
        
        # Execute query
        results = await db_service.execute_query(query_params)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Prepare response
        response = FilteredQueryResponse(
            filters_applied=query_params,
            results=results,
            total_results=len(results),
            execution_time=execution_time,
            pagination={
                "limit": request.limit,
                "offset": request.offset,
                "total": len(results)
            }
        )
        
        # Cache result
        await cache_service.set(cache_key, response.dict(), ttl=3600)
        
        return response
        
    except Exception as e:
        logger.error(f"Error filtering problems: {e}")
        raise HTTPException(status_code=500, detail=f"Filtering failed: {str(e)}")

@router.post("/bulk", response_model=BulkQueryResponse)
async def process_bulk_queries(
    request: BulkQueryRequest,
    db_service: DatabaseService = Depends(get_database_service),
    nlp_service: NLPService = Depends(get_nlp_service),
    cache_service: CompanyDataCacheManager = Depends(get_cache_service)
):
    """
    Process multiple queries in a single request
    
    Useful for batch processing or comparing results across multiple queries
    """
    try:
        start_time = time.time()
        
        results = []
        errors = []
        successful_queries = 0
        
        for query_text in request.queries:
            try:
                # Process each query
                query_request = QueryRequest(query=query_text, use_cache=request.use_cache)
                
                # Check cache first
                cache_key = f"query:{hash(query_text)}"
                if request.use_cache:
                    cached_result = await cache_service.get(cache_key)
                    if cached_result:
                        cached_result['cached'] = True
                        results.append(QueryResponse(**cached_result))
                        successful_queries += 1
                        continue
                
                # Parse and execute query
                parsed_intent = await nlp_service.parse_query(query_text)
                query_results = await db_service.execute_query(parsed_intent)
                
                query_response = QueryResponse(
                    query=query_text,
                    parsed_intent=parsed_intent,
                    results=query_results,
                    total_results=len(query_results),
                    execution_time=0,  # Individual timing not calculated in bulk
                    cached=False
                )
                
                results.append(query_response)
                successful_queries += 1
                
                # Cache result
                if request.use_cache:
                    await cache_service.set(cache_key, query_response.dict(), ttl=3600)
                
            except Exception as e:
                logger.error(f"Error processing bulk query '{query_text}': {e}")
                errors.append(ErrorResponse(
                    error="QueryProcessingError",
                    message=f"Failed to process query: {query_text}",
                    details={"query": query_text, "error": str(e)}
                ))
        
        # Calculate total execution time
        execution_time = time.time() - start_time
        
        return BulkQueryResponse(
            results=results,
            total_queries=len(request.queries),
            successful_queries=successful_queries,
            failed_queries=len(errors),
            errors=errors,
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error processing bulk queries: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk query processing failed: {str(e)}")

@router.get("/suggest", response_model=SuggestionResponse)
async def get_query_suggestions(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db_service: DatabaseService = Depends(get_database_service),
    nlp_service: NLPService = Depends(get_nlp_service),
    cache_service: CompanyDataCacheManager = Depends(get_cache_service)
):
    """
    Get query suggestions based on partial input
    
    Example: Input "easy array" might suggest ["easy array questions", "easy array Google problems"]
    """
    try:
        start_time = time.time()
        
        # Check cache first
        cache_key = f"suggest:{hash(query + str(limit))}"
        cached_result = await cache_service.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for suggestion query: {query}")
            return SuggestionResponse(**cached_result)
        
        # Generate suggestions using NLP service
        suggestions = await nlp_service.generate_suggestions(query, limit=limit)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Prepare response
        response = SuggestionResponse(
            query=query,
            suggestions=suggestions,
            total_suggestions=len(suggestions),
            execution_time=execution_time
        )
        
        # Cache result
        await cache_service.set(cache_key, response.dict(), ttl=3600)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating suggestions for query '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Suggestion generation failed: {str(e)}")

@router.get("/autocomplete", response_model=AutocompleteResponse)
async def get_autocomplete_suggestions(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db_service: DatabaseService = Depends(get_database_service),
    nlp_service: NLPService = Depends(get_nlp_service),
    cache_service: CompanyDataCacheManager = Depends(get_cache_service)
):
    """
    Get autocomplete suggestions for query input
    
    Example: Input "dynamic" might suggest ["dynamic programming", "dynamic programming hard"]
    """
    try:
        start_time = time.time()
        
        # Check cache first
        cache_key = f"autocomplete:{hash(query + str(limit))}"
        cached_result = await cache_service.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for autocomplete query: {query}")
            return AutocompleteResponse(**cached_result)
        
        # Generate autocomplete suggestions using NLP service
        suggestions = await nlp_service.generate_autocomplete(query, limit=limit)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Prepare response
        response = AutocompleteResponse(
            query=query,
            suggestions=suggestions,
            total_suggestions=len(suggestions),
            execution_time=execution_time
        )
        
        # Cache result
        await cache_service.set(cache_key, response.dict(), ttl=3600)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating autocomplete for query '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Autocomplete generation failed: {str(e)}")
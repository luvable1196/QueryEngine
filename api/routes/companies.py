from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import time

from ..services.database_service import DatabaseService
from ..models.request_models import FilterRequest
from ..models.response_models import (
    FilteredQueryResponse,
    CompanyStatsResponse,
    CompanyStats,
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


class CompaniesResponse(BaseModel):
    companies: List[CompanyStats]
    count: int

@router.get("/", response_model=CompaniesResponse)
async def get_all_companies(
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Retrieve a list of all companies with their statistics
    """
    try:
        start_time = time.time()
        
        # Fetch all companies
        companies = await db_service.get_all_companies()
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        logger.info(f"Retrieved {len(companies)} companies in {execution_time:.3f} seconds")
        return {"companies": companies, "count": len(companies)}
        
    except Exception as e:
        logger.error(f"Error retrieving companies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve companies: {str(e)}")
    


@router.get("/{company_name}/problems")
async def get_company_by_name(
    company_name: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Retrieve all problems associated with a specific company
    """
    try:
        start_time = time.time()
        
        # Get company stats (which includes problems)
        company_stats = await db_service.get_company_by_name(company_name)
        print(f"Company stats for {company_name}: {company_stats}")
        
        if not company_stats:
            raise HTTPException(
                status_code=404, 
                detail=f"Company '{company_name}' not found"
            )
        
        # Extract problems from CompanyStats object
        problems = getattr(company_stats, 'problems', [])
        print(f"Problems for {company_name}: {problems}")
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Build response with safe attribute access
        response_data = {
        "company": company_name,
        "company_stats": {
            "name": getattr(company_stats, 'name', company_name),
            "problem_count": getattr(company_stats, 'problem_count', 0),
            "avg_frequency": getattr(company_stats, 'avg_frequency', 0),
            "easy_count": getattr(company_stats, 'easy_count', 0),
            "medium_count": getattr(company_stats, 'medium_count', 0),
            "hard_count": getattr(company_stats, 'hard_count', 0),
            "difficulty_distribution": getattr(company_stats, 'difficulty_distribution', {}),
            "most_common_topics": getattr(company_stats, 'most_common_topics', []),
            "average_acceptance_rate": getattr(company_stats, 'average_acceptance_rate', 0),
        },
        "problems": problems,
        "total_problems": len(problems) if problems is not None else 0,  # Safe length check
        "execution_time": execution_time,
        "timestamp": datetime.now()
    }
        
        # Add optional attributes if they exist
        if hasattr(company_stats, 'total_problems'):
            response_data["company_stats"]["total_problems"] = company_stats.total_problems
        if hasattr(company_stats, 'problems_by_difficulty'):
            response_data["company_stats"]["problems_by_difficulty"] = company_stats.problems_by_difficulty
        if hasattr(company_stats, 'average_frequency'):
            response_data["company_stats"]["average_frequency"] = company_stats.average_frequency
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving problems for company '{company_name}': {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve problems for company '{company_name}'"
        )
    

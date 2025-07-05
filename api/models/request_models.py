from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SortBy(str, Enum):
    FREQUENCY = "frequency"
    ACCEPTANCE_RATE = "acceptance_rate"
    TITLE = "title"
    DIFFICULTY = "difficulty"
    QUESTION_NUMBER = "question_number"

class QueryRequest(BaseModel):
    """
    Main query request model for natural language processing
    """
    query: str = Field(..., description="Natural language query", min_length=1, max_length=500)
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    use_cache: bool = Field(default=True, description="Whether to use cached results")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "query": "give me easy array questions asked by Google",
                "context": {"user_id": "123", "session_id": "abc"},
                "use_cache": True
            }
        }

class FilterRequest(BaseModel):
    """
    Advanced filtering request model
    """
    difficulty: Optional[List[DifficultyLevel]] = Field(
        default=None, 
        description="Filter by difficulty levels"
    )
    topics: Optional[List[str]] = Field(
        default=None, 
        description="Filter by programming topics"
    )
    companies: Optional[List[str]] = Field(
        default=None, 
        description="Filter by companies"
    )
    min_frequency: Optional[float] = Field(
        default=None, 
        ge=0, 
        le=100,
        description="Minimum frequency threshold"
    )
    max_frequency: Optional[float] = Field(
        default=None, 
        ge=0, 
        le=100,
        description="Maximum frequency threshold"
    )
    min_acceptance_rate: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0,
        description="Minimum acceptance rate (0.0 to 1.0)"
    )
    max_acceptance_rate: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0,
        description="Maximum acceptance rate (0.0 to 1.0)"
    )
    question_numbers: Optional[List[int]] = Field(
        default=None,
        description="Filter by specific question numbers"
    )
    sort_by: Optional[SortBy] = Field(
        default=SortBy.FREQUENCY,
        description="Sort results by field"
    )
    sort_order: Optional[SortOrder] = Field(
        default=SortOrder.DESC,
        description="Sort order"
    )
    limit: Optional[int] = Field(
        default=50, 
        ge=1, 
        le=1000,
        description="Maximum number of results"
    )
    offset: Optional[int] = Field(
        default=0,
        ge=0,
        description="Offset for pagination"
    )
    
    @validator('topics')
    def validate_topics(cls, v):
        if v:
            return [topic.strip() for topic in v if topic.strip()]
        return v
    
    @validator('companies')
    def validate_companies(cls, v):
        if v:
            return [company.strip() for company in v if company.strip()]
        return v
    
    @validator('min_frequency', 'max_frequency')
    def validate_frequency_range(cls, v, values):
        if v is not None and v < 0:
            raise ValueError('Frequency cannot be negative')
        return v
    
    @validator('max_frequency')
    def validate_frequency_order(cls, v, values):
        if v is not None and 'min_frequency' in values and values['min_frequency'] is not None:
            if v < values['min_frequency']:
                raise ValueError('max_frequency must be greater than or equal to min_frequency')
        return v
    
    @validator('max_acceptance_rate')
    def validate_acceptance_rate_order(cls, v, values):
        if v is not None and 'min_acceptance_rate' in values and values['min_acceptance_rate'] is not None:
            if v < values['min_acceptance_rate']:
                raise ValueError('max_acceptance_rate must be greater than or equal to min_acceptance_rate')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "difficulty": ["easy", "medium"],
                "topics": ["Array", "Two Pointers"],
                "companies": ["Google", "Amazon"],
                "min_frequency": 10.0,
                "max_frequency": 100.0,
                "min_acceptance_rate": 0.3,
                "max_acceptance_rate": 0.9,
                "sort_by": "frequency",
                "sort_order": "desc",
                "limit": 20,
                "offset": 0
            }
        }

class CompanyStatsRequest(BaseModel):
    """
    Request model for company statistics
    """
    company_name: str = Field(..., description="Name of the company")
    include_problems: bool = Field(
        default=False, 
        description="Whether to include problem list in response"
    )
    difficulty_filter: Optional[List[DifficultyLevel]] = Field(
        default=None,
        description="Filter problems by difficulty"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=100,
        description="Limit number of problems returned"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "company_name": "Google",
                "include_problems": True,
                "difficulty_filter": ["easy", "medium"],
                "limit": 10
            }
        }

class BulkQueryRequest(BaseModel):
    """
    Request model for bulk queries
    """
    queries: List[str] = Field(
        ..., 
        description="List of queries to process",
        min_items=1,
        max_items=10
    )
    use_cache: bool = Field(default=True, description="Whether to use cached results")
    
    @validator('queries')
    def validate_queries(cls, v):
        if not v:
            raise ValueError('Queries list cannot be empty')
        return [query.strip() for query in v if query.strip()]
    
    class Config:
        schema_extra = {
            "example": {
                "queries": [
                    "give me easy array questions",
                    "show me hard tree problems",
                    "find Google interview questions"
                ],
                "use_cache": True
            }
        }
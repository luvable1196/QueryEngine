from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ProblemResult(BaseModel):
    """
    Individual problem result model
    """
    question_number: Optional[int] = Field(description="LeetCode question number")
    title: str = Field(description="Problem title")
    difficulty: DifficultyLevel = Field(description="Problem difficulty level")
    frequency: float = Field(description="Frequency score (0-100)")
    acceptance_rate: float = Field(description="Acceptance rate (0.0-1.0)")
    link: str = Field(description="LeetCode problem URL")
    topics: List[str] = Field(description="Programming topics/techniques")
    companies: List[str] = Field(description="Companies that ask this question")
    
    class Config:
        schema_extra = {
            "example": {
                "question_number": 206,
                "title": "Reverse Linked List",
                "difficulty": "easy",
                "frequency": 100.0,
                "acceptance_rate": 0.792066,
                "link": "https://leetcode.com/problems/reverse-linked-list",
                "topics": ["Linked List", "Recursion"],
                "companies": ["Amazon", "Google", "Microsoft"]
            }
        }

class QueryResponse(BaseModel):
    """
    Main query response model
    """
    query: str = Field(description="Original query string")
    parsed_intent: Dict[str, Any] = Field(description="Parsed query intent and filters")
    results: List[ProblemResult] = Field(description="List of matching problems")
    total_results: int = Field(description="Total number of results found")
    execution_time: float = Field(description="Query execution time in seconds")
    cached: bool = Field(description="Whether result was served from cache")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    pagination: Optional[Dict[str, int]] = Field(default=None, description="Pagination info")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "give me easy array questions asked by Google",
                "parsed_intent": {
                    "difficulty": ["easy"],
                    "topics": ["Array"],
                    "companies": ["Google"],
                    "intent": "find_problems"
                },
                "results": [],
                "total_results": 15,
                "execution_time": 0.125,
                "cached": False,
                "pagination": {
                    "limit": 50,
                    "offset": 0,
                    "total": 15
                }
            }
        }

class CompanyStats(BaseModel):
    """
    Company statistics model
    """
    name: str = Field(description="Company name")
    problem_count: int = Field(description="Total number of problems")
    avg_frequency: float = Field(description="Average frequency score")
    easy_count: int = Field(description="Number of easy problems")
    medium_count: int = Field(description="Number of medium problems")
    hard_count: int = Field(description="Number of hard problems")
    difficulty_distribution: Optional[Dict[str, int]] = Field(
        default=None, 
        description="Problems by difficulty"
    )
    most_common_topics: Optional[List[str]] = Field(
        default=None, 
        description="Most frequently asked topics"
    )
    average_acceptance_rate: Optional[float] = Field(
        default=None, 
        description="Average acceptance rate"
    )
    problems: Optional[List[ProblemResult]] = Field(
        default=None, 
        description="List of problems (if requested)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Google",
                "problem_count": 150,
                "avg_frequency": 67.5,
                "easy_count": 45,
                "medium_count": 75,
                "hard_count": 30,
                "difficulty_distribution": {
                    "easy": 45,
                    "medium": 75,
                    "hard": 30
                },
                "most_common_topics": [
                    "Array", "Dynamic Programming", "Tree", "Graph", "String"
                ],
                "average_acceptance_rate": 0.58,
                "problems": None
            }
        }

class TopicStats(BaseModel):
    """
    Topic statistics model
    """
    name: str = Field(description="Topic name")
    problem_count: int = Field(description="Number of problems")
    avg_frequency: float = Field(description="Average frequency score")
    easy_count: int = Field(description="Number of easy problems")
    medium_count: int = Field(description="Number of medium problems")
    hard_count: int = Field(description="Number of hard problems")
    difficulty_distribution: Optional[Dict[str, int]] = Field(
        default=None, 
        description="Problems by difficulty"
    )
    average_acceptance_rate: Optional[float] = Field(
        default=None, 
        description="Average acceptance rate"
    )
    top_companies: Optional[List[str]] = Field(
        default=None, 
        description="Companies that ask this topic most"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Array",
                "problem_count": 250,
                "avg_frequency": 72.3,
                "easy_count": 80,
                "medium_count": 120,
                "hard_count": 50,
                "difficulty_distribution": {
                    "easy": 80,
                    "medium": 120,
                    "hard": 50
                },
                "average_acceptance_rate": 0.62,
                "top_companies": ["Google", "Amazon", "Microsoft", "Apple", "Facebook"]
            }
        }

class HealthResponse(BaseModel):
    """
    Health check response model
    """
    status: str = Field(description="Service status")
    message: str = Field(description="Status message")
    timestamp: datetime = Field(default_factory=datetime.now)
    database_connected: bool = Field(description="Database connection status")
    cache_connected: bool = Field(description="Cache connection status")
    total_problems: int = Field(description="Total problems in database")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "message": "LeetCode Query System is running",
                "database_connected": True,
                "cache_connected": True,
                "total_problems": 2500
            }
        }

class ErrorResponse(BaseModel):
    """
    Error response model
    """
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid query parameters",
                "details": {
                    "field": "difficulty",
                    "value": "invalid_difficulty"
                }
            }
        }

class SuggestionResponse(BaseModel):
    """
    Query suggestion response model
    """
    suggestions: List[str] = Field(description="List of suggested queries")
    categories: Dict[str, List[str]] = Field(description="Suggestions by category")
    
    class Config:
        schema_extra = {
            "example": {
                "suggestions": [
                    "Give me easy array questions",
                    "Show me hard dynamic programming problems",
                    "Find Google interview questions"
                ],
                "categories": {
                    "difficulty": [
                        "easy problems",
                        "medium problems", 
                        "hard problems"
                    ],
                    "topics": [
                        "array questions",
                        "tree problems",
                        "graph algorithms"
                    ],
                    "companies": [
                        "Google questions",
                        "Amazon problems",
                        "Microsoft interviews"
                    ]
                }
            }
        }

class BulkQueryResponse(BaseModel):
    """
    Bulk query response model
    """
    results: List[QueryResponse] = Field(description="Results for each query")
    total_queries: int = Field(description="Total number of queries processed")
    successful_queries: int = Field(description="Number of successful queries")
    failed_queries: int = Field(description="Number of failed queries")
    execution_time: float = Field(description="Total execution time")
    errors: Optional[List[ErrorResponse]] = Field(
        default=None, 
        description="List of errors for failed queries"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "results": [],
                "total_queries": 3,
                "successful_queries": 3,
                "failed_queries": 0,
                "execution_time": 0.456,
                "errors": None
            }
        }

class WebSocketMessage(BaseModel):
    """
    WebSocket message model
    """
    type: str = Field(description="Message type")
    data: Dict[str, Any] = Field(description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "type": "query_result",
                "data": {
                    "query": "easy array problems",
                    "result_count": 25
                }
            }
        }

class CompanyStatsResponse(BaseModel):
    """
    Company statistics response model
    """
    company_name: str = Field(description="Company name")
    stats: CompanyStats = Field(description="Company statistics")
    problems: Optional[List[ProblemResult]] = Field(
        default=None, 
        description="List of problems (if requested)"
    )
    execution_time: float = Field(description="Query execution time")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "company_name": "Google",
                "stats": {
                    "name": "Google",
                    "problem_count": 150,
                    "avg_frequency": 67.5,
                    "easy_count": 45,
                    "medium_count": 75,
                    "hard_count": 30
                },
                "problems": None,
                "execution_time": 0.045
            }
        }

class TopicStatsResponse(BaseModel):
    """
    Topic statistics response model
    """
    topic_name: str = Field(description="Topic name")
    stats: TopicStats = Field(description="Topic statistics")
    problems: Optional[List[ProblemResult]] = Field(
        default=None, 
        description="List of problems (if requested)"
    )
    execution_time: float = Field(description="Query execution time")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "topic_name": "Array",
                "stats": {
                    "name": "Array",
                    "problem_count": 250,
                    "avg_frequency": 72.3,
                    "easy_count": 80,
                    "medium_count": 120,
                    "hard_count": 50
                },
                "problems": None,
                "execution_time": 0.032
            }
        }

class DatabaseStatsResponse(BaseModel):
    """
    Database statistics response model
    """
    total_problems: int = Field(description="Total number of problems")
    problems_by_difficulty: Dict[str, int] = Field(description="Problems count by difficulty")
    total_companies: int = Field(description="Total number of companies")
    total_topics: int = Field(description="Total number of topics")
    average_frequency: float = Field(description="Average frequency across all problems")
    average_acceptance_rate: float = Field(description="Average acceptance rate")
    last_updated: datetime = Field(description="Last database update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "total_problems": 2500,
                "problems_by_difficulty": {
                    "easy": 850,
                    "medium": 1200,
                    "hard": 450
                },
                "total_companies": 150,
                "total_topics": 75,
                "average_frequency": 42.5,
                "average_acceptance_rate": 0.58,
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }

class FilteredQueryResponse(BaseModel):
    """
    Response model for filtered queries
    """
    filters_applied: Dict[str, Any] = Field(description="Filters that were applied")
    results: List[ProblemResult] = Field(description="List of matching problems")
    total_results: int = Field(description="Total number of results found")
    execution_time: float = Field(description="Query execution time in seconds")
    pagination: Optional[Dict[str, int]] = Field(default=None, description="Pagination info")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "filters_applied": {
                    "difficulty": ["easy", "medium"],
                    "topics": ["Array"],
                    "companies": ["Google"],
                    "min_frequency": 50.0
                },
                "results": [],
                "total_results": 32,
                "execution_time": 0.089,
                "pagination": {
                    "limit": 20,
                    "offset": 0,
                    "total": 32
                }
            }
        }

class CacheStats(BaseModel):
    """
    Cache statistics model
    """
    total_queries: int = Field(description="Total queries processed")
    cache_hits: int = Field(description="Number of cache hits")
    cache_misses: int = Field(description="Number of cache misses")
    hit_rate: float = Field(description="Cache hit rate percentage")
    cache_size: int = Field(description="Current cache size")
    
    class Config:
        schema_extra = {
            "example": {
                "total_queries": 1000,
                "cache_hits": 750,
                "cache_misses": 250,
                "hit_rate": 0.75,
                "cache_size": 500
            }
        }

class SystemStatsResponse(BaseModel):
    """
    System statistics response model
    """
    database_stats: DatabaseStatsResponse = Field(description="Database statistics")
    cache_stats: CacheStats = Field(description="Cache statistics")
    uptime: str = Field(description="System uptime")
    version: str = Field(description="System version")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "database_stats": {
                    "total_problems": 2500,
                    "problems_by_difficulty": {"easy": 850, "medium": 1200, "hard": 450},
                    "total_companies": 150,
                    "total_topics": 75,
                    "average_frequency": 42.5,
                    "average_acceptance_rate": 0.58,
                    "last_updated": "2024-01-15T10:30:00Z"
                },
                "cache_stats": {
                    "total_queries": 1000,
                    "cache_hits": 750,
                    "cache_misses": 250,
                    "hit_rate": 0.75,
                    "cache_size": 500
                },
                "uptime": "2 days, 14 hours, 32 minutes",
                "version": "1.0.0"
            }
        }

class ValidationErrorResponse(BaseModel):
    """
    Validation error response model
    """
    error: str = Field(default="ValidationError", description="Error type")
    message: str = Field(description="Error message")
    field_errors: Dict[str, List[str]] = Field(description="Field-specific validation errors")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Request validation failed",
                "field_errors": {
                    "difficulty": ["Invalid difficulty level"],
                    "min_frequency": ["Must be between 0 and 100"]
                }
            }
        }

class SearchSuggestion(BaseModel):
    """
    Individual search suggestion model
    """
    text: str = Field(description="Suggestion text")
    type: str = Field(description="Suggestion type (company, topic, difficulty)")
    count: int = Field(description="Number of related problems")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Array",
                "type": "topic",
                "count": 250
            }
        }

class AutocompleteResponse(BaseModel):
    """
    Autocomplete response model
    """
    query: str = Field(description="Original query string")
    suggestions: List[SearchSuggestion] = Field(description="List of suggestions")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "arr",
                "suggestions": [
                    {"text": "Array", "type": "topic", "count": 250},
                    {"text": "Binary Search", "type": "topic", "count": 150}
                ]
            }
        }
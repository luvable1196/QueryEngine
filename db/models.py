from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class Problem(BaseModel):
    """
    Core problem model representing a LeetCode problem
    """
    id: Optional[int] = None
    question_number: Optional[int] = None
    title: str
    difficulty: DifficultyLevel
    frequency: float
    acceptance_rate: float
    link: str
    topics: List[str]
    companies: List[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True

class Company(BaseModel):
    """
    Company model for storing company information
    """
    id: Optional[int] = None
    name: str
    total_problems: int = 0
    difficulty_distribution: Dict[str, int] = {}
    most_common_topics: List[str] = []
    created_at: Optional[datetime] = None
    
class Topic(BaseModel):
    """
    Topic model for storing programming topics
    """
    id: Optional[int] = None
    name: str
    problem_count: int = 0
    average_difficulty: float = 0.0
    created_at: Optional[datetime] = None

class QueryLog(BaseModel):
    """
    Model for logging user queries
    """
    id: Optional[int] = None
    query: str
    parsed_intent: Dict[str, Any]
    execution_time: float
    result_count: int
    created_at: Optional[datetime] = None
    
class DatabaseSchema:
    """
    Database schema definitions
    """
    
    CREATE_PROBLEMS_TABLE = """
    CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY,
        question_number INTEGER,
        title VARCHAR NOT NULL,
        difficulty VARCHAR NOT NULL,
        frequency DOUBLE NOT NULL,
        acceptance_rate DOUBLE NOT NULL,
        link VARCHAR NOT NULL,
        topics VARCHAR NOT NULL,  -- JSON array as string
        companies VARCHAR NOT NULL,  -- JSON array as string
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_COMPANIES_TABLE = """
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY,
        name VARCHAR UNIQUE NOT NULL,
        total_problems INTEGER DEFAULT 0,
        difficulty_distribution VARCHAR,  -- JSON as string
        most_common_topics VARCHAR,  -- JSON array as string
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_TOPICS_TABLE = """
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY,
        name VARCHAR UNIQUE NOT NULL,
        problem_count INTEGER DEFAULT 0,
        average_difficulty DOUBLE DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_QUERY_LOGS_TABLE = """
    CREATE TABLE IF NOT EXISTS query_logs (
        id INTEGER PRIMARY KEY,
        query VARCHAR NOT NULL,
        parsed_intent VARCHAR NOT NULL,  -- JSON as string
        execution_time DOUBLE NOT NULL,
        result_count INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_problems_difficulty ON problems(difficulty);",
        "CREATE INDEX IF NOT EXISTS idx_problems_frequency ON problems(frequency);",
        "CREATE INDEX IF NOT EXISTS idx_problems_acceptance_rate ON problems(acceptance_rate);",
        "CREATE INDEX IF NOT EXISTS idx_problems_question_number ON problems(question_number);",
        "CREATE INDEX IF NOT EXISTS idx_problems_title ON problems(title);",
        "CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);",
        "CREATE INDEX IF NOT EXISTS idx_topics_name ON topics(name);",
        "CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at);"
    ]
    
    @classmethod
    def get_all_schemas(cls) -> List[str]:
        """Get all table creation statements"""
        return [
            cls.CREATE_PROBLEMS_TABLE,
            cls.CREATE_COMPANIES_TABLE,
            cls.CREATE_TOPICS_TABLE,
            cls.CREATE_QUERY_LOGS_TABLE
        ] + cls.CREATE_INDEXES
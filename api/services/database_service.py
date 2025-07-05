import os
import json
import pandas as pd
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import time
import re

from ..models.request_models import FilterRequest
from ..models.response_models import ProblemResult, CompanyStats, TopicStats
from db.connection import db_connection
from db.models import Problem, Company, Topic, QueryLog
from .cache_service import CompanyDataCacheManager
import redis.asyncio as redis


logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Database service for managing LeetCode problems data
    """
    
    def __init__(self, data_path: str = "./data"):
        self.data_path = Path(data_path)
        self.db = db_connection
        self.batch_size = 1000
        self.cache_manager = CompanyDataCacheManager(
            max_queries=50,
            frequency_threshold=2,
            recency_threshold_hours=100
        )

    # async def initialize_cache(self):
    #     """Initialize the cache manager"""
    #     await self.cache_manager.initialize()
        
    async def initialize(self) -> None:
        """Initialize database connection and schema"""
        try:
            await self.db.connect()
            await self.db.initialize_schema()
            try:
                redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True
                )
                await self.cache_manager.initialize(redis_client)
                logger.info("Cache manager initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize cache manager: {e}")
            
            # Check if data already exists
            existing_count = await self.db.get_table_count("problems")
            
            if existing_count == 0:
                logger.info("No existing data found. Loading data from files...")
                await self.load_data_from_files()
            else:
                logger.info(f"Database already contains {existing_count} problems. Skipping data loading.")
                # Update stats in case they're missing
                # await self._update_company_stats()
                # await self._update_topic_stats()
                
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database): {e}")
    
    async def close(self) -> None:
        """Close database connection"""
        await self.db.disconnect()
    
    async def load_data_from_files(self) -> None:
        """Load data from CSV/Excel files in the data directory"""
        try:
            if not self.data_path.exists():
                logger.warning(f"Data directory {self.data_path} does not exist")
                return
            
            # Get total count before loading
            initial_count = await self.db.get_table_count("problems")
            logger.info(f"Initial problem count: {initial_count}")
            
            # Load data from all company directories
            total_loaded = 0
            for company_dir in self.data_path.iterdir():
                if company_dir.is_dir():
                    loaded = await self._load_company_data(company_dir)
                    total_loaded += loaded
                    logger.info(f"Loaded {loaded} problems from {company_dir.name}")
            
            # Get final count
            final_count = await self.db.get_table_count("problems")
            logger.info(f"Data loading completed. Total problems: {final_count} (loaded: {total_loaded})")
            
        except Exception as e:
            logger.error(f"Error loading data from files: {e}")
    
    async def _load_company_data(self, company_dir: Path) -> int:
        """Load data for a specific company"""
        company_name = company_dir.name
        loaded_count = 0
        
        try:
            # Process all CSV and Excel files in the company directory
            for file_path in company_dir.glob("*.csv"):
                count = await self._load_file_data(file_path, company_name)
                loaded_count += count
            
            for file_path in company_dir.glob("*.xlsx"):
                count = await self._load_file_data(file_path, company_name)
                loaded_count += count
            
            return loaded_count
            
        except Exception as e:
            logger.error(f"Error loading data for company {company_name}: {e}")
            return 0
    
    async def _load_file_data(self, file_path: Path, company_name: str) -> int:
        """Load data from a single file"""
        try:
            # Read file based on extension
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                logger.warning(f"Unsupported file format: {file_path}")
                return 0
            
            # Clean and validate data
            df = await self._clean_dataframe(df, company_name)
            
            if df.empty:
                logger.warning(f"No valid data found in {file_path}")
                return 0
            
            # Convert to Problem objects and insert
            problems = await self._dataframe_to_problems(df, company_name)
            await self._insert_problems_batch(problems)
            
            logger.info(f"Loaded {len(problems)} problems from {file_path}")
            return len(problems)
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return 0
    
    async def _clean_dataframe(self, df: pd.DataFrame, company_name: str) -> pd.DataFrame:
        """Clean and validate DataFrame"""
        try:
            # Strip whitespace from column names
            df.columns = df.columns.str.strip()
            
            # Rename columns to standard format - Updated for your data structure
            column_mapping = {
                'Title': 'title',
                'Difficulty': 'difficulty',
                'Frequency': 'frequency',
                'Acceptance Rate': 'acceptance_rate',
                'Link': 'link',
                'Topics': 'topics',
                'Question Number': 'question_number',
                'Problem Number': 'question_number',
                'Leetcode Link': 'link',
                'LeetCode Link': 'link'
            }
            
            # Apply column mapping
            df = df.rename(columns=column_mapping)
            
            # Ensure required columns exist
            required_columns = ['title', 'difficulty', 'frequency', 'acceptance_rate', 'link', 'topics']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.warning(f"Missing columns in data: {missing_columns}")
                return pd.DataFrame()  # Return empty DataFrame
            
            # Clean data
            df = df.dropna(subset=['title', 'difficulty', 'link'])
            
            # Standardize difficulty values
            df['difficulty'] = df['difficulty'].str.strip().str.upper()
            df = df[df['difficulty'].isin(['EASY', 'MEDIUM', 'HARD'])]
            
            # Clean frequency values
            df['frequency'] = pd.to_numeric(df['frequency'], errors='coerce')
            df = df.dropna(subset=['frequency'])
            
            # Clean acceptance rate values
            df['acceptance_rate'] = pd.to_numeric(df['acceptance_rate'], errors='coerce')
            df = df.dropna(subset=['acceptance_rate'])
            
            # Your data already has decimal format (0.792066), so no conversion needed
            # But add validation to ensure values are between 0 and 1
            df = df[(df['acceptance_rate'] >= 0) & (df['acceptance_rate'] <= 1)]
            
            # Clean topics - handle comma-separated values
            df['topics'] = df['topics'].fillna('').astype(str).str.strip()
            
            # Extract question number from link - FIXED REGEX
            if 'question_number' not in df.columns:
                # Extract the problem slug from the URL and create a hash-based ID
                # Since your URLs don't contain numbers, we'll create a unique identifier
                df['question_number'] = df['link'].apply(self._extract_problem_id)
            
            # Add company information
            df['companies'] = df.apply(lambda x: [company_name], axis=1)
            
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning dataframe: {e}")
            return pd.DataFrame()
    
    def _extract_problem_id(self, link: str) -> Optional[int]:
        """Extract or generate a unique problem ID from the link"""
        try:
            # First try to extract number from URL (some problems might have numbers)
            number_match = re.search(r'/problems/[^/]*?(\d+)', link)
            if number_match:
                return int(number_match.group(1))
            
            # If no number, extract the problem slug and create a hash
            slug_match = re.search(r'/problems/([^/?]+)', link)
            if slug_match:
                slug = slug_match.group(1)
                # Create a simple hash-based ID (you might want to use a proper hash function)
                return abs(hash(slug)) % 10000000  # Limit to 7 digits
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting problem ID from {link}: {e}")
            return None
    
    async def _dataframe_to_problems(self, df: pd.DataFrame, company_name: str) -> List[Problem]:
        """Convert DataFrame to Problem objects"""
        problems = []
        
        for _, row in df.iterrows():
            try:
                # Parse topics - handle comma-separated values
                topics = []
                if isinstance(row['topics'], str) and row['topics'].strip():
                    # Split by comma and clean each topic
                    topics = [t.strip() for t in row['topics'].split(',') if t.strip()]
                
                # Parse companies
                companies = []
                if 'companies' in row and row['companies']:
                    companies = row['companies']
                else:
                    companies = [company_name]
                
                # Validate JSON serialization before creating Problem object
                try:
                    json.dumps(topics)
                    json.dumps(companies)
                except (TypeError, ValueError) as e:
                    logger.warning(f"JSON serialization failed for row {row.get('title', 'unknown')}: {e}")
                    continue
                
                problem = Problem(
                    question_number=int(row['question_number']) if pd.notna(row['question_number']) else None,
                    title=str(row['title']).strip(),
                    difficulty=row['difficulty'],
                    frequency=float(row['frequency']),
                    acceptance_rate=float(row['acceptance_rate']),
                    link=str(row['link']).strip(),
                    topics=topics,
                    companies=companies,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                problems.append(problem)
                
            except Exception as e:
                logger.warning(f"Error processing row: {e}")
                logger.warning(f"Row data: {row.to_dict()}")
                continue
        
        return problems
    
    async def _insert_problems_batch(self, problems: List[Problem]) -> None:
        """Insert problems in batches with conflict handling"""
        if not problems:
            return
        
        # Use INSERT OR IGNORE to handle duplicates based on title and link
        insert_query = """
        INSERT OR IGNORE INTO problems (
            question_number, title, difficulty, frequency, acceptance_rate, 
            link, topics, companies, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Process in batches
        for i in range(0, len(problems), self.batch_size):
            batch = problems[i:i + self.batch_size]
            
            # Prepare parameters
            params = []
            for problem in batch:
                params.append([
                    problem.question_number,
                    problem.title,
                    problem.difficulty.value if hasattr(problem.difficulty, 'value') else problem.difficulty,
                    problem.frequency,
                    problem.acceptance_rate,
                    problem.link,
                    json.dumps(problem.topics),
                    json.dumps(problem.companies),
                    problem.created_at,
                    problem.updated_at
                ])
            
            await self.db.execute_many(insert_query, params)
    
    async def execute_query(self, parsed_query: Dict[str, Any]) -> List[ProblemResult]:
        """Execute a parsed query and return results"""
        try:
            start_time = time.time()
            
            # Build SQL query
            sql_query, params = await self._build_sql_query(parsed_query)
            
            # Execute query
            results = await self.db.execute_query(sql_query, params)
            
            # Convert to ProblemResult objects
            problem_results = []
            for row in results:
                problem_result = ProblemResult(
                    question_number=row.get('question_number'),
                    title=row['title'],
                    difficulty=row['difficulty'].lower(),
                    frequency=row['frequency'],
                    acceptance_rate=row['acceptance_rate'],
                    link=row['link'],
                    topics=json.loads(row['topics']) if row['topics'] else [],
                    companies=json.loads(row['companies']) if row['companies'] else []
                )
                problem_results.append(problem_result)
            
            # Log query execution
            execution_time = time.time() - start_time
            await self._log_query_execution(parsed_query, len(problem_results), execution_time)
            
            return problem_results
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []  # ADD THIS LINE - was missing

    
    async def _build_sql_query(self, parsed_query: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Build SQL query from parsed query parameters"""
        base_query = "SELECT * FROM problems WHERE 1=1"
        params = []
        conditions = []
        
        # Add difficulty filter
        if 'difficulty' in parsed_query and parsed_query['difficulty']:
            difficulties = [d.upper() for d in parsed_query['difficulty']]
            placeholders = ','.join(['?' for _ in difficulties])
            conditions.append(f"difficulty IN ({placeholders})")
            params.extend(difficulties)
        
        # Add company filter
        if 'companies' in parsed_query and parsed_query['companies']:
            company_conditions = []
            for company in parsed_query['companies']:
                company_conditions.append("companies LIKE ?")
                params.append(f'%"{company}"%')
            conditions.append(f"({' OR '.join(company_conditions)})")
        
        # Add topic filter
        if 'topics' in parsed_query and parsed_query['topics']:
            topic_conditions = []
            for topic in parsed_query['topics']:
                topic_conditions.append("topics LIKE ?")
                params.append(f'%"{topic}"%')
            conditions.append(f"({' OR '.join(topic_conditions)})")
        
        # Add frequency filter
        if 'min_frequency' in parsed_query and parsed_query['min_frequency'] is not None:
            conditions.append("frequency >= ?")
            params.append(parsed_query['min_frequency'])
        
        if 'max_frequency' in parsed_query and parsed_query['max_frequency'] is not None:
            conditions.append("frequency <= ?")
            params.append(parsed_query['max_frequency'])
        
        # Add acceptance rate filter
        if 'min_acceptance_rate' in parsed_query and parsed_query['min_acceptance_rate'] is not None:
            conditions.append("acceptance_rate >= ?")
            params.append(parsed_query['min_acceptance_rate'])
        
        if 'max_acceptance_rate' in parsed_query and parsed_query['max_acceptance_rate'] is not None:
            conditions.append("acceptance_rate <= ?")
            params.append(parsed_query['max_acceptance_rate'])
        
        # Add search term filter
        if 'search_term' in parsed_query and parsed_query['search_term']:
            search_term = f"%{parsed_query['search_term']}%"
            conditions.append("(title LIKE ? OR topics LIKE ?)")
            params.extend([search_term, search_term])
        
        # Combine conditions
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        # Add sorting
        sort_by = parsed_query.get('sort_by', 'frequency')
        sort_order = parsed_query.get('sort_order', 'DESC')
        
        if sort_by in ['frequency', 'acceptance_rate', 'difficulty', 'title']:
            base_query += f" ORDER BY {sort_by} {sort_order}"
        
        # Add limit
        if 'limit' in parsed_query and parsed_query['limit']:
            base_query += " LIMIT ?"
            params.append(parsed_query['limit'])
        
        return base_query, params
    
    async def _log_query_execution(self, parsed_query: Dict[str, Any], result_count: int, execution_time: float) -> None:
        """Log query execution details"""
        try:
            query_log = QueryLog(
                query_params=json.dumps(parsed_query),
                result_count=result_count,
                execution_time=execution_time,
                timestamp=datetime.now()
            )
            
            # Insert into query log table
            insert_query = """
            INSERT INTO query_logs (query_params, result_count, execution_time, timestamp)
            VALUES (?, ?, ?, ?)
            """
            
            await self.db.execute(insert_query, [
                query_log.query_params,
                query_log.result_count,
                query_log.execution_time,
                query_log.timestamp
            ])
            
        except Exception as e:
            logger.warning(f"Failed to log query execution: {e}")

    async def get_companies(self) -> List[CompanyStats]:
        """Get all companies with their problem counts and enhanced statistics - with smart cache"""
        try:
            # Try to get from cache first
            cache_key_params = {"type": "all_companies_stats"}
            cached_companies = await self.cache_manager.get_cached_query(cache_key_params)
            
            if cached_companies:
                logger.info("Smart cache hit for companies data")
                # Convert back to CompanyStats objects
                companies = []
                for company_data in cached_companies:
                    company_stats = CompanyStats(**company_data)
                    companies.append(company_stats)
                return companies
            
            logger.info("Smart cache miss - fetching from database")
            
            # Your existing database query logic
            query = """
            SELECT 
                companies,
                frequency,
                acceptance_rate,
                difficulty
            FROM problems
            WHERE companies IS NOT NULL 
            AND companies != '' 
            AND companies != '[]'
            """
            
            results = await self.db.execute_query(query)
            
            # Parse companies in Python instead of SQL
            company_data = {}
            
            for row in results:
                try:
                    # Parse JSON companies list
                    companies_json = row['companies']
                    if isinstance(companies_json, str):
                        companies_list = json.loads(companies_json)
                    else:
                        companies_list = companies_json if companies_json else []
                    
                    # Process each company in the list
                    for company_name in companies_list:
                        if company_name and company_name.strip():
                            company_name = company_name.strip()
                            
                            if company_name not in company_data:
                                company_data[company_name] = {
                                    'problem_count': 0,
                                    'frequencies': [],
                                    'acceptance_rates': [],
                                    'easy_count': 0,
                                    'medium_count': 0,
                                    'hard_count': 0
                                }
                            
                            # Add problem data
                            company_data[company_name]['problem_count'] += 1
                            company_data[company_name]['frequencies'].append(row['frequency'])
                            company_data[company_name]['acceptance_rates'].append(row['acceptance_rate'])
                            
                            # Count difficulty
                            difficulty = row['difficulty'].upper()
                            if difficulty == 'EASY':
                                company_data[company_name]['easy_count'] += 1
                            elif difficulty == 'MEDIUM':
                                company_data[company_name]['medium_count'] += 1
                            elif difficulty == 'HARD':
                                company_data[company_name]['hard_count'] += 1
                                
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Error parsing companies JSON: {e}")
                    continue
            
            # Convert to CompanyStats objects
            companies = []
            companies_for_cache = []  # For caching
            
            for company_name, data in company_data.items():
                # Calculate averages
                avg_frequency = sum(data['frequencies']) / len(data['frequencies']) if data['frequencies'] else 0
                avg_acceptance_rate = sum(data['acceptance_rates']) / len(data['acceptance_rates']) if data['acceptance_rates'] else 0
                
                # Get most common topics for this company (simplified version)
                most_common_topics = await self._get_company_top_topics_simple(company_name)
                
                # Create difficulty distribution
                difficulty_distribution = {
                    "easy": data['easy_count'],
                    "medium": data['medium_count'],
                    "hard": data['hard_count']
                }
                
                company_stats = CompanyStats(
                    name=company_name,
                    problem_count=data['problem_count'],
                    avg_frequency=round(avg_frequency, 2),
                    easy_count=data['easy_count'],
                    medium_count=data['medium_count'],
                    hard_count=data['hard_count'],
                    difficulty_distribution=difficulty_distribution,
                    most_common_topics=most_common_topics,
                    average_acceptance_rate=round(avg_acceptance_rate, 4),
                    problems=None
                )
                companies.append(company_stats)
                
                # Prepare for caching (convert to dict)
                companies_for_cache.append({
                    'name': company_name,
                    'problem_count': data['problem_count'],
                    'avg_frequency': round(avg_frequency, 2),
                    'easy_count': data['easy_count'],
                    'medium_count': data['medium_count'],
                    'hard_count': data['hard_count'],
                    'difficulty_distribution': difficulty_distribution,
                    'most_common_topics': most_common_topics,
                    'average_acceptance_rate': round(avg_acceptance_rate, 4),
                    'problems': None
                })
            
            # Sort by problem count (descending)
            companies.sort(key=lambda x: x.problem_count, reverse=True)
            companies_for_cache.sort(key=lambda x: x['problem_count'], reverse=True)
            
            # Cache the results using smart cache
            await self.cache_manager.cache_query_result(cache_key_params, companies_for_cache)
            logger.info(f"Smart cached {len(companies)} companies data")
            
            return companies
        
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            return []

    async def clear_query_cache(self):
        """Clear the smart query cache"""
        try:
            result = await self.cache_manager.clear_cache()
            logger.info("Smart query cache cleared")
            return result
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return {"error": str(e)}

    async def get_cache_stats(self):
        """Get smart cache statistics"""
        try:
            analytics = await self.cache_manager.get_cache_analytics()
            memory_usage = await self.cache_manager.get_memory_usage()
            
            return {
                "cache_analytics": analytics,
                "memory_usage": memory_usage,
                "cache_type": "smart_lru_with_frequency"
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}

    async def _get_company_top_topics_simple(self, company_name: str, limit: int = 5) -> List[str]:
        """Get the most common topics for a specific company - simplified version"""
        try:
            # Get all problems for this company
            query = """
            SELECT topics
            FROM problems
            WHERE companies LIKE ?
            AND topics IS NOT NULL 
            AND topics != '' 
            AND topics != '[]'
            """
            
            # Use LIKE pattern for company matching
            company_pattern = f'%"{company_name}"%'
            results = await self.db.execute_query(query, [company_pattern])
            
            # Count topics in Python
            topic_counts = {}
            for row in results:
                try:
                    topics_json = row['topics']
                    if isinstance(topics_json, str):
                        topics_list = json.loads(topics_json)
                    else:
                        topics_list = topics_json if topics_json else []
                    
                    for topic in topics_list:
                        if topic and topic.strip():
                            topic = topic.strip()
                            topic_counts[topic] = topic_counts.get(topic, 0) + 1
                            
                except (json.JSONDecodeError, TypeError):
                    continue
            
            # Sort by count and return top topics
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            return [topic for topic, count in sorted_topics[:limit]]
        
        except Exception as e:
            logger.warning(f"Error getting top topics for company {company_name}: {e}")
            return []
    
    async def get_topics(self) -> List[TopicStats]:
        """Get all topics with their problem counts"""
        try:
            query = """
            SELECT 
                topic_name,
                COUNT(*) as problem_count,
                AVG(frequency) as avg_frequency,
                COUNT(CASE WHEN difficulty = 'EASY' THEN 1 END) as easy_count,
                COUNT(CASE WHEN difficulty = 'MEDIUM' THEN 1 END) as medium_count,
                COUNT(CASE WHEN difficulty = 'HARD' THEN 1 END) as hard_count
            FROM (
                SELECT 
                    json_extract(topics_json.value, '$') as topic_name,
                    frequency,
                    difficulty
                FROM problems, json_each(problems.topics) as topics_json
                WHERE problems.topics != '' 
                AND problems.topics != '[]' 
                AND json_valid(problems.topics)
            )
            WHERE topic_name IS NOT NULL AND topic_name != ''
            GROUP BY topic_name
            ORDER BY problem_count DESC
            """
            
            results = await self.db.execute_query(query)
            
            topics = []
            for row in results:
                topic_stats = TopicStats(
                    name=row['topic_name'],
                    problem_count=row['problem_count'],
                    avg_frequency=row['avg_frequency'],
                    easy_count=row['easy_count'],
                    medium_count=row['medium_count'],
                    hard_count=row['hard_count']
                )
                topics.append(topic_stats)
            
            return topics
            
        except Exception as e:
            logger.error(f"Error getting topics: {e}")
            return []
        

    async def get_company_by_name(self, company_name: str) -> Optional[CompanyStats]:
        """Get company with smart indexing and cache invalidation"""
        try:
            # Input validation
            if not company_name or not company_name.strip():
                return None
            
            company_name_clean = company_name.strip()
            
            # Check if index exists and is valid
            if not hasattr(self, '_company_index') or not self._company_index:
                await self._build_company_index()
            
            # Try to get from index
            result = self._company_index.get(company_name_clean.lower())
            
            if result:
                logger.debug(f"Company '{company_name_clean}' found in index")
                return result
            
            # If not found, try fuzzy matching for common variations
            fuzzy_result = await self._fuzzy_match_company(company_name_clean)
            if fuzzy_result:
                logger.info(f"Fuzzy match found for '{company_name_clean}': {fuzzy_result.name}")
                return fuzzy_result
            
            logger.debug(f"Company '{company_name_clean}' not found")
            return None
            
        except Exception as e:
            logger.error(f"Error getting company by name '{company_name}': {e}")
            return None

    async def _build_company_index(self):
        """Build the company index from cache or database"""
        try:
            logger.info("Building company index...")
            companies = await self.get_companies()  # This hits your smart cache
            self._company_index = {c.name.lower(): c for c in companies}
            self._company_index_timestamp = time.time()
            logger.info(f"Company index built with {len(self._company_index)} companies")
        except Exception as e:
            logger.error(f"Error building company index: {e}")
            self._company_index = {}

    async def _fuzzy_match_company(self, company_name: str) -> Optional[CompanyStats]:
        """Attempt fuzzy matching for company names"""
        try:
            if not self._company_index:
                return None
            
            company_lower = company_name.lower()
            
            # Try exact match with different cases
            for indexed_name, company_stats in self._company_index.items():
                # Check if the input is contained in the indexed name or vice versa
                if (company_lower in indexed_name or 
                    indexed_name in company_lower or
                    # Handle common variations
                    company_lower.replace(' ', '') == indexed_name.replace(' ', '') or
                    company_lower.replace('-', '').replace('_', '') == indexed_name.replace('-', '').replace('_', '')):
                    return company_stats
            
            return None
            
        except Exception as e:
            logger.error(f"Error in fuzzy matching for '{company_name}': {e}")
            return None

    async def invalidate_company_index(self):
        """Invalidate the company index (call this when data changes)"""
        try:
            if hasattr(self, '_company_index'):
                delattr(self, '_company_index')
            if hasattr(self, '_company_index_timestamp'):
                delattr(self, '_company_index_timestamp')
            logger.info("Company index invalidated")
        except Exception as e:
            logger.error(f"Error invalidating company index: {e}")

    async def get_all_company_names(self) -> List[str]:
        """Get list of all company names (useful for autocomplete)"""
        try:
            if not hasattr(self, '_company_index') or not self._company_index:
                await self._build_company_index()
            
            return [company.name for company in self._company_index.values()]
            
        except Exception as e:
            logger.error(f"Error getting all company names: {e}")
            return []

    async def search_companies(self, query: str, limit: int = 10) -> List[CompanyStats]:
        """Search companies by name (partial matching)"""
        try:
            if not query or not query.strip():
                return []
            
            if not hasattr(self, '_company_index') or not self._company_index:
                await self._build_company_index()
            
            query_lower = query.strip().lower()
            matches = []
            
            for company in self._company_index.values():
                if query_lower in company.name.lower():
                    matches.append(company)
            
            # Sort by relevance (exact matches first, then by problem count)
            matches.sort(key=lambda x: (
                not x.name.lower().startswith(query_lower),  # Exact prefix matches first
                -x.problem_count  # Then by problem count descending
            ))
            
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Error searching companies with query '{query}': {e}")
            return []

        
    async def get_all_companies(self) -> List[CompanyStats]:
        """Get all companies with their problem counts - alias for get_companies"""
        return await self.get_companies()

    
    async def get_problem_by_id(self, problem_id: int) -> Optional[ProblemResult]:
        """Get a specific problem by ID"""
        try:
            query = "SELECT * FROM problems WHERE id = ?"
            results = await self.db.execute_query(query, [problem_id])
            
            if not results:
                return None
            
            row = results[0]
            return ProblemResult(
                question_number=row.get('question_number'),
                title=row['title'],
                difficulty=row['difficulty'].lower(),
                frequency=row['frequency'],
                acceptance_rate=row['acceptance_rate'],
                link=row['link'],
                topics=json.loads(row['topics']) if row['topics'] else [],
                companies=json.loads(row['companies']) if row['companies'] else []
            )
            
        except Exception as e:
            logger.error(f"Error getting problem by ID {problem_id}: {e}")
            return None
    
    async def get_problem_by_title(self, title: str) -> Optional[ProblemResult]:
        """Get a specific problem by title"""
        try:
            query = "SELECT * FROM problems WHERE title = ?"
            results = await self.db.execute_query(query, [title])
            
            if not results:
                return None
            
            row = results[0]
            return ProblemResult(
                question_number=row.get('question_number'),
                title=row['title'],
                difficulty=row['difficulty'].lower(),
                frequency=row['frequency'],
                acceptance_rate=row['acceptance_rate'],
                link=row['link'],
                topics=json.loads(row['topics']) if row['topics'] else [],
                companies=json.loads(row['companies']) if row['companies'] else []
            )
            
        except Exception as e:
            logger.error(f"Error getting problem by title {title}: {e}")
            return None
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get general database statistics"""
        try:
            stats = {}
            
            # Total problems
            total_problems = await self.db.get_table_count("problems")
            stats['total_problems'] = total_problems
            
            # Problems by difficulty
            difficulty_query = """
            SELECT difficulty, COUNT(*) as count
            FROM problems
            GROUP BY difficulty
            """
            difficulty_results = await self.db.execute_query(difficulty_query)
            stats['problems_by_difficulty'] = {row['difficulty']: row['count'] for row in difficulty_results}
            
            # Total companies
            company_count = await self.db.get_table_count("companies")
            stats['total_companies'] = company_count
            
            # Total topics
            topic_count = await self.db.get_table_count("topics")
            stats['total_topics'] = topic_count
            
            # Average frequency
            avg_freq_query = "SELECT AVG(frequency) as avg_frequency FROM problems"
            avg_freq_result = await self.db.execute_query(avg_freq_query)
            stats['average_frequency'] = avg_freq_result[0]['avg_frequency'] if avg_freq_result else 0
            
            # Average acceptance rate
            avg_acc_query = "SELECT AVG(acceptance_rate) as avg_acceptance_rate FROM problems"
            avg_acc_result = await self.db.execute_query(avg_acc_query)
            stats['average_acceptance_rate'] = avg_acc_result[0]['avg_acceptance_rate'] if avg_acc_result else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the database service"""
        try:
            # Check database connection
            test_query = "SELECT 1"
            await self.db.execute_query(test_query)
            
            # Get basic stats
            stats = await self.get_stats()
            
            return {
                'status': 'healthy',
                'database_connected': True,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'database_connected': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
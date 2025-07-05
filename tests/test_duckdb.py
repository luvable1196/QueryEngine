#!/usr/bin/env python3
"""
DuckDB Database Test Script
This script connects to your DuckDB database and inspects its contents
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

# Assuming your db connection is in this path - adjust if needed
import sys
sys.path.append('.')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DuckDBTester:
    def __init__(self, db_path: str = "leetcode_data.db"):
        self.db_path = db_path
        self.db = None
        
    async def connect(self):
        """Connect to DuckDB"""
        try:
            # Import your database connection
            from db.connection import db_connection
            self.db = db_connection
            await self.db.connect()
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.db:
            await self.db.disconnect()
            logger.info("Disconnected from database")
    
    async def get_basic_info(self) -> Dict[str, Any]:
        """Get basic database information"""
        info = {}
        
        try:
            # Get all tables
            tables_query = """
            SELECT table_name, estimated_size 
            FROM information_schema.tables 
            WHERE table_schema = 'main'
            """
            tables = await self.db.execute_query(tables_query)
            info['tables'] = tables
            logger.info(f"Found {len(tables)} tables")
            
            # Get table counts
            table_counts = {}
            for table in tables:
                table_name = table['table_name']
                try:
                    count = await self.db.get_table_count(table_name)
                    table_counts[table_name] = count
                except Exception as e:
                    table_counts[table_name] = f"Error: {e}"
            
            info['table_counts'] = table_counts
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting basic info: {e}")
            return {'error': str(e)}
    
    async def inspect_problems_table(self) -> Dict[str, Any]:
        """Inspect the problems table in detail"""
        result = {}
        
        try:
            # Get table schema
            schema_query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'problems'
            ORDER BY ordinal_position
            """
            schema = await self.db.execute_query(schema_query)
            result['schema'] = schema
            
            # Get total count
            total_count = await self.db.get_table_count('problems')
            result['total_count'] = total_count
            
            # Get sample data (first 5 rows)
            sample_query = "SELECT * FROM problems LIMIT 5"
            sample_data = await self.db.execute_query(sample_query)
            result['sample_data'] = sample_data
            
            # Check for JSON validity issues
            json_check_query = """
            SELECT 
                COUNT(*) as total_rows,
                COUNT(CASE WHEN json_valid(companies) THEN 1 END) as valid_companies,
                COUNT(CASE WHEN json_valid(topics) THEN 1 END) as valid_topics,
                COUNT(CASE WHEN NOT json_valid(companies) THEN 1 END) as invalid_companies,
                COUNT(CASE WHEN NOT json_valid(topics) THEN 1 END) as invalid_topics
            FROM problems
            """
            json_check = await self.db.execute_query(json_check_query)
            result['json_validation'] = json_check[0] if json_check else None
            
            # Get difficulty distribution
            difficulty_query = """
            SELECT difficulty, COUNT(*) as count
            FROM problems
            GROUP BY difficulty
            ORDER BY count DESC
            """
            difficulty_dist = await self.db.execute_query(difficulty_query)
            result['difficulty_distribution'] = difficulty_dist
            
            # Get examples of invalid JSON (if any)
            invalid_companies_query = """
            SELECT id, title, companies
            FROM problems 
            WHERE NOT json_valid(companies)
            LIMIT 3
            """
            invalid_companies = await self.db.execute_query(invalid_companies_query)
            result['invalid_companies_examples'] = invalid_companies
            
            invalid_topics_query = """
            SELECT id, title, topics
            FROM problems 
            WHERE NOT json_valid(topics)
            LIMIT 3
            """
            invalid_topics = await self.db.execute_query(invalid_topics_query)
            result['invalid_topics_examples'] = invalid_topics
            
            return result
            
        except Exception as e:
            logger.error(f"Error inspecting problems table: {e}")
            return {'error': str(e)}
    
    async def test_company_query(self) -> Dict[str, Any]:
        """Test the company query that's failing"""
        result = {}
        
        try:
            # Try the original failing query
            logger.info("Testing original company query...")
            original_query = """
            SELECT 
                json_extract(value, '$') as company_name,
                COUNT(*) as problem_count,
                AVG(frequency) as avg_frequency,
                COUNT(CASE WHEN difficulty = 'EASY' THEN 1 END) as easy_count,
                COUNT(CASE WHEN difficulty = 'MEDIUM' THEN 1 END) as medium_count,
                COUNT(CASE WHEN difficulty = 'HARD' THEN 1 END) as hard_count
            FROM problems, json_each(problems.companies)
            GROUP BY company_name
            ORDER BY problem_count DESC
            LIMIT 5
            """
            
            try:
                original_result = await self.db.execute_query(original_query)
                result['original_query'] = {'success': True, 'data': original_result}
            except Exception as e:
                result['original_query'] = {'success': False, 'error': str(e)}
            
            # Try the fixed query with JSON validation
            logger.info("Testing fixed company query...")
            fixed_query = """
            SELECT 
                json_extract(value, '$') as company_name,
                COUNT(*) as problem_count,
                AVG(frequency) as avg_frequency,
                COUNT(CASE WHEN difficulty = 'EASY' THEN 1 END) as easy_count,
                COUNT(CASE WHEN difficulty = 'MEDIUM' THEN 1 END) as medium_count,
                COUNT(CASE WHEN difficulty = 'HARD' THEN 1 END) as hard_count
            FROM problems, json_each(problems.companies)
            WHERE json_valid(problems.companies) AND json_valid(problems.topics)
            GROUP BY company_name
            ORDER BY problem_count DESC
            LIMIT 5
            """
            
            try:
                fixed_result = await self.db.execute_query(fixed_query)
                result['fixed_query'] = {'success': True, 'data': fixed_result}
            except Exception as e:
                result['fixed_query'] = {'success': False, 'error': str(e)}
            
            return result
            
        except Exception as e:
            logger.error(f"Error testing company query: {e}")
            return {'error': str(e)}
    
    async def test_topics_query(self) -> Dict[str, Any]:
        """Test the topics query that's failing"""
        result = {}
        
        try:
            # Try the original failing query
            logger.info("Testing original topics query...")
            original_query = """
            SELECT 
                json_extract(value, '$') as topic_name,
                COUNT(*) as problem_count,
                AVG(frequency) as avg_frequency,
                COUNT(CASE WHEN difficulty = 'EASY' THEN 1 END) as easy_count,
                COUNT(CASE WHEN difficulty = 'MEDIUM' THEN 1 END) as medium_count,
                COUNT(CASE WHEN difficulty = 'HARD' THEN 1 END) as hard_count
            FROM problems, json_each(problems.topics)
            WHERE json_extract(value, '$') != ''
            GROUP BY topic_name
            ORDER BY problem_count DESC
            LIMIT 5
            """
            
            try:
                original_result = await self.db.execute_query(original_query)
                result['original_query'] = {'success': True, 'data': original_result}
            except Exception as e:
                result['original_query'] = {'success': False, 'error': str(e)}
            
            # Try the fixed query with JSON validation
            logger.info("Testing fixed topics query...")
            fixed_query = """
            SELECT 
                json_extract(value, '$') as topic_name,
                COUNT(*) as problem_count,
                AVG(frequency) as avg_frequency,
                COUNT(CASE WHEN difficulty = 'EASY' THEN 1 END) as easy_count,
                COUNT(CASE WHEN difficulty = 'MEDIUM' THEN 1 END) as medium_count,
                COUNT(CASE WHEN difficulty = 'HARD' THEN 1 END) as hard_count
            FROM problems, json_each(problems.topics)
            WHERE json_extract(value, '$') != '' AND json_valid(problems.topics) AND json_valid(problems.companies)
            GROUP BY topic_name
            ORDER BY problem_count DESC
            LIMIT 5
            """
            
            try:
                fixed_result = await self.db.execute_query(fixed_query)
                result['fixed_query'] = {'success': True, 'data': fixed_result}
            except Exception as e:
                result['fixed_query'] = {'success': False, 'error': str(e)}
            
            return result
            
        except Exception as e:
            logger.error(f"Error testing topics query: {e}")
            return {'error': str(e)}
    
    def print_results(self, results: Dict[str, Any], title: str):
        """Pretty print results"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
        
        if isinstance(results, dict):
            for key, value in results.items():
                print(f"\n{key.upper().replace('_', ' ')}:")
                print("-" * 40)
                
                if isinstance(value, list):
                    for item in value[:5]:  # Show first 5 items
                        print(f"  {item}")
                    if len(value) > 5:
                        print(f"  ... and {len(value) - 5} more")
                elif isinstance(value, dict):
                    for k, v in value.items():
                        print(f"  {k}: {v}")
                else:
                    print(f"  {value}")
        else:
            print(results)

async def main():
    """Run all tests"""
    tester = DuckDBTester()
    
    # Connect to database
    if not await tester.connect():
        return
    
    try:
        # Test 1: Basic database info
        logger.info("Getting basic database information...")
        basic_info = await tester.get_basic_info()
        tester.print_results(basic_info, "BASIC DATABASE INFO")
        
        # Test 2: Inspect problems table
        logger.info("Inspecting problems table...")
        problems_info = await tester.inspect_problems_table()
        tester.print_results(problems_info, "PROBLEMS TABLE INSPECTION")
        
        # Test 3: Test company query
        logger.info("Testing company queries...")
        company_test = await tester.test_company_query()
        tester.print_results(company_test, "COMPANY QUERY TEST")
        
        # Test 4: Test topics query
        logger.info("Testing topics queries...")
        topics_test = await tester.test_topics_query()
        tester.print_results(topics_test, "TOPICS QUERY TEST")
        
    finally:
        await tester.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SQLiteInspector:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from database")
    
    def get_table_names(self) -> List[str]:
        """Get all table names in the database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            return tables
        except Exception as e:
            logger.error(f"Error getting table names: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> List[Dict]:
        """Get column information for a specific table"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'cid': row[0],
                    'name': row[1],
                    'type': row[2],
                    'notnull': row[3],
                    'dflt_value': row[4],
                    'pk': row[5]
                })
            return columns
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return []
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict]:
        """Get sample data from a table"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting sample data from {table_name}: {e}")
            return []
    
    def test_json_columns(self, table_name: str) -> Dict[str, Any]:
        """Test JSON columns in a table"""
        results = {}
        try:
            # Get table info first
            columns = self.get_table_info(table_name)
            
            # Check each column for JSON data
            cursor = self.connection.cursor()
            for column in columns:
                col_name = column['name']
                try:
                    # Try to get a sample of non-null values
                    cursor.execute(f"SELECT {col_name} FROM {table_name} WHERE {col_name} IS NOT NULL LIMIT 5;")
                    sample_values = [row[0] for row in cursor.fetchall()]
                    
                    # Test if values are JSON
                    json_valid = []
                    for value in sample_values:
                        try:
                            if isinstance(value, str):
                                json.loads(value)
                                json_valid.append(True)
                            else:
                                json_valid.append(False)
                        except (json.JSONDecodeError, TypeError):
                            json_valid.append(False)
                    
                    results[col_name] = {
                        'sample_values': sample_values,
                        'json_valid': json_valid,
                        'all_json': all(json_valid) if json_valid else False
                    }
                except Exception as e:
                    results[col_name] = {'error': str(e)}
            
            return results
        except Exception as e:
            logger.error(f"Error testing JSON columns in {table_name}: {e}")
            return {'error': str(e)}
    
    def safe_json_query(self, query: str) -> Dict[str, Any]:
        """Execute a query safely, handling JSON parsing issues"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                row_dict = dict(row)
                # Try to parse JSON fields
                for key, value in row_dict.items():
                    if isinstance(value, str):
                        try:
                            # Try to parse as JSON
                            parsed = json.loads(value)
                            row_dict[key] = parsed
                        except json.JSONDecodeError:
                            # Keep as string if not valid JSON
                            pass
                results.append(row_dict)
            
            return {'success': True, 'data': results, 'count': len(results)}
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {'success': False, 'error': str(e)}

def main():
    # Initialize inspector
    inspector = SQLiteInspector('leetcode_data.db')
    
    if not inspector.connect():
        return
    
    try:
        print("=" * 60)
        print("  SQLITE DATABASE INSPECTION")
        print("=" * 60)
        
        # Get all table names
        tables = inspector.get_table_names()
        print(f"Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
        print()
        
        # Inspect each table
        for table_name in tables:
            print("=" * 60)
            print(f"  TABLE: {table_name}")
            print("=" * 60)
            
            # Get table structure
            columns = inspector.get_table_info(table_name)
            print("COLUMNS:")
            print("-" * 40)
            for col in columns:
                print(f"  {col['name']} ({col['type']}) - PK: {bool(col['pk'])}, NOT NULL: {bool(col['notnull'])}")
            print()
            
            # Get sample data
            sample_data = inspector.get_sample_data(table_name, 3)
            print("SAMPLE DATA:")
            print("-" * 40)
            for i, row in enumerate(sample_data, 1):
                print(f"Row {i}:")
                for key, value in row.items():
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  {key}: {value[:100]}...")
                    else:
                        print(f"  {key}: {value}")
                print()
            
            # Test JSON columns
            json_results = inspector.test_json_columns(table_name)
            print("JSON COLUMN ANALYSIS:")
            print("-" * 40)
            for col_name, result in json_results.items():
                if 'error' in result:
                    print(f"  {col_name}: ERROR - {result['error']}")
                else:
                    json_status = "Valid JSON" if result['all_json'] else "Mixed/Non-JSON"
                    print(f"  {col_name}: {json_status}")
            print()
        
        # Test company queries with fixed syntax
        print("=" * 60)
        print("  TESTING COMPANY QUERIES")
        print("=" * 60)
        
        # Check if problems table exists and has company-related columns
        if 'problems' in tables:
            columns = inspector.get_table_info('problems')
            column_names = [col['name'] for col in columns]
            
            print("Available columns in problems table:")
            for col_name in column_names:
                print(f"  - {col_name}")
            print()
            
            # Try different approaches to query companies
            company_queries = [
                "SELECT COUNT(*) as total_problems FROM problems",
                "SELECT * FROM problems LIMIT 3",
            ]
            
            # If there are JSON columns, try JSON queries
            json_columns = []
            for col_name in column_names:
                if 'company' in col_name.lower() or 'companies' in col_name.lower():
                    json_columns.append(col_name)
            
            if json_columns:
                print(f"Found potential company columns: {json_columns}")
                for col_name in json_columns:
                    # Test if column contains JSON
                    test_query = f"SELECT {col_name} FROM problems WHERE {col_name} IS NOT NULL LIMIT 3"
                    company_queries.append(test_query)
            
            for i, query in enumerate(company_queries, 1):
                print(f"Query {i}: {query}")
                result = inspector.safe_json_query(query)
                print(f"Result: {result}")
                print()
        
        # Test topics queries
        print("=" * 60)
        print("  TESTING TOPICS QUERIES")
        print("=" * 60)
        
        if 'problems' in tables:
            columns = inspector.get_table_info('problems')
            column_names = [col['name'] for col in columns]
            
            # Look for topic-related columns
            topic_columns = []
            for col_name in column_names:
                if 'topic' in col_name.lower() or 'tag' in col_name.lower() or 'category' in col_name.lower():
                    topic_columns.append(col_name)
            
            if topic_columns:
                print(f"Found potential topic columns: {topic_columns}")
                for col_name in topic_columns:
                    query = f"SELECT {col_name} FROM problems WHERE {col_name} IS NOT NULL LIMIT 5"
                    print(f"Query: {query}")
                    result = inspector.safe_json_query(query)
                    print(f"Result: {result}")
                    print()
            else:
                print("No obvious topic columns found")
        
    finally:
        inspector.disconnect()

if __name__ == "__main__":
    main()
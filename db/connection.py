import sqlite3
import aiosqlite
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .models import DatabaseSchema

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Async database connection manager for SQLite
    """
    
    def __init__(self, db_path: str = "leetcode_data.db"):
        self.db_path = db_path
        self.connection = None
        self.is_connected = False
        
    async def connect(self) -> None:
        """Establish database connection"""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            self.connection.row_factory = aiosqlite.Row
            self.is_connected = True
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            self.is_connected = False
            logger.info("Database connection closed")
    
    async def initialize_schema(self) -> None:
        """Initialize database schema"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Create tables and indexes
            schemas = DatabaseSchema.get_all_schemas()
            
            for schema in schemas:
                await self.connection.execute(schema)
            
            await self.connection.commit()
            logger.info("Database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise
    
    async def execute(self, query: str, params: Optional[List[Any]] = None) -> None:
        """Execute a single query"""
        try:
            if not self.is_connected:
                await self.connect()
            
            if params:
                await self.connection.execute(query, params)
            else:
                await self.connection.execute(query)
            
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise
    
    async def execute_many(self, query: str, params_list: List[List[Any]]) -> None:
        """Execute query with multiple parameter sets"""
        try:
            if not self.is_connected:
                await self.connect()
            
            await self.connection.executemany(query, params_list)
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to execute many queries: {e}")
            raise
    
    async def execute_query(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        try:
            if not self.is_connected:
                await self.connect()
            
            if params:
                cursor = await self.connection.execute(query, params)
            else:
                cursor = await self.connection.execute(query)
            
            rows = await cursor.fetchall()
            
            # Convert rows to dictionaries
            result = []
            for row in rows:
                result.append(dict(row))
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise
    
    async def get_table_count(self, table_name: str) -> int:
        """Get count of records in a table"""
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = await self.execute_query(query)
            return result[0]['count'] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to get table count for {table_name}: {e}")
            return 0
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        try:
            query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
            """
            result = await self.execute_query(query, [table_name])
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"Failed to check table existence: {e}")
            return False
    
    async def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get table schema information"""
        try:
            query = f"PRAGMA table_info({table_name})"
            result = await self.execute_query(query)
            return result
            
        except Exception as e:
            logger.error(f"Failed to get table schema for {table_name}: {e}")
            return []
    
    async def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Create backup using sqlite3 backup API
            backup_conn = await aiosqlite.connect(backup_path)
            await self.connection.backup(backup_conn)
            await backup_conn.close()
            
            logger.info(f"Database backup created: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    async def optimize_database(self) -> None:
        """Optimize database performance"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Run optimization commands
            await self.connection.execute("VACUUM")
            await self.connection.execute("ANALYZE")
            await self.connection.commit()
            
            logger.info("Database optimization completed")
            
        except Exception as e:
            logger.error(f"Failed to optimize database: {e}")
            raise
    
    async def get_database_size(self) -> int:
        """Get database file size in bytes"""
        try:
            db_file = Path(self.db_path)
            if db_file.exists():
                return db_file.stat().st_size
            return 0
            
        except Exception as e:
            logger.error(f"Failed to get database size: {e}")
            return 0
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information"""
        try:
            info = {
                'database_path': self.db_path,
                'connected': self.is_connected,
                'file_size': await self.get_database_size(),
                'tables': {},
                'last_modified': None
            }
            
            # Get file modification time
            db_file = Path(self.db_path)
            if db_file.exists():
                info['last_modified'] = datetime.fromtimestamp(db_file.stat().st_mtime)
            
            # Get table information
            if self.is_connected:
                tables_query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """
                tables = await self.execute_query(tables_query)
                
                for table in tables:
                    table_name = table['name']
                    info['tables'][table_name] = {
                        'count': await self.get_table_count(table_name),
                        'schema': await self.get_table_schema(table_name)
                    }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {'error': str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            health = {
                'status': 'healthy',
                'connected': self.is_connected,
                'readable': False,
                'writable': False,
                'response_time': None,
                'error': None
            }
            
            start_time = asyncio.get_event_loop().time()
            
            # Test connection
            if not self.is_connected:
                await self.connect()
            
            # Test read operation
            test_query = "SELECT 1 as test"
            await self.execute_query(test_query)
            health['readable'] = True
            
            # Test write operation
            await self.execute("CREATE TEMP TABLE IF NOT EXISTS health_test (id INTEGER)")
            await self.execute("INSERT INTO health_test (id) VALUES (1)")
            await self.execute("DROP TABLE health_test")
            health['writable'] = True
            
            # Calculate response time
            end_time = asyncio.get_event_loop().time()
            health['response_time'] = end_time - start_time
            
            return health
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'connected': False,
                'readable': False,
                'writable': False,
                'response_time': None,
                'error': str(e)
            }

# Global database connection instance
db_connection = DatabaseConnection()
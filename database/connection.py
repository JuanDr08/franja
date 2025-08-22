import psycopg2
from psycopg2 import pool
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any
import time


class DatabaseConnection:
    """Handles PostgreSQL connections with timeout and error handling."""
    
    def __init__(self, config: Dict[str, Any], 
                 min_connections: int = 1, 
                 max_connections: int = 5,
                 connection_timeout: int = 30):
        """
        Initialize database connection manager.
        
        Args:
            config: Database connection configuration
            min_connections: Minimum connections in pool
            max_connections: Maximum connections in pool
            connection_timeout: Connection timeout in seconds
        """
        self.config = config
        self.connection_timeout = connection_timeout
        self.connection_pool: Optional[pool.ThreadedConnectionPool] = None
        
        # Build connection string
        self.connection_string = (
            f"host={config['host']} "
            f"port={config['port']} "
            f"dbname={config['database']} "
            f"user={config['username']} "
            f"password={config['password']} "
            f"connect_timeout={connection_timeout}"
        )
        
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                self.connection_string
            )
            logging.info("Database connection pool created successfully")
        except psycopg2.Error as e:
            logging.error(f"Failed to create connection pool: {e}")
            raise
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test database connection.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            start_time = time.time()
            
            # Test basic connection
            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            elapsed_time = time.time() - start_time
            
            return True, f"Connection successful. PostgreSQL version: {version[:50]}... (Response time: {elapsed_time:.2f}s)"
            
        except psycopg2.OperationalError as e:
            if "timeout" in str(e).lower():
                return False, f"Connection timeout after {self.connection_timeout} seconds"
            else:
                return False, f"Connection failed: {str(e)}"
        except psycopg2.Error as e:
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for getting database connections from pool.
        
        Yields:
            Database connection
        """
        connection = None
        try:
            if not self.connection_pool:
                raise Exception("Connection pool not initialized")
            
            connection = self.connection_pool.getconn()
            if connection.closed:
                raise psycopg2.OperationalError("Connection is closed")
            
            yield connection
            
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            logging.error(f"Database connection error: {e}")
            raise
        except Exception as e:
            if connection:
                connection.rollback()
            logging.error(f"Unexpected error with database connection: {e}")
            raise
        finally:
            if connection and self.connection_pool:
                self.connection_pool.putconn(connection)
    
    def execute_query(self, query: str, params: tuple = None, 
                     fetch_results: bool = True) -> list:
        """
        Execute SQL query safely with parameters.
        
        Args:
            query: SQL query with placeholders
            params: Query parameters
            fetch_results: Whether to fetch and return results
            
        Returns:
            Query results or empty list
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Set query timeout
                cursor.execute(f"SET statement_timeout = '{self.connection_timeout * 1000}';")
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch_results:
                    results = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    cursor.close()
                    return results, columns
                else:
                    conn.commit()
                    cursor.close()
                    return [], []
                    
        except psycopg2.Error as e:
            logging.error(f"Query execution error: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during query execution: {e}")
            raise
    
    def close_pool(self):
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            logging.info("Database connection pool closed")
    
    def get_pool_status(self) -> Dict[str, int]:
        """
        Get connection pool status.
        
        Returns:
            Dictionary with pool statistics
        """
        if not self.connection_pool:
            return {"error": "Pool not initialized"}
        
        try:
            return {
                "total_connections": len(self.connection_pool._pool + self.connection_pool._used),
                "available_connections": len(self.connection_pool._pool),
                "used_connections": len(self.connection_pool._used)
            }
        except:
            return {"error": "Unable to get pool status"}
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate database configuration.
        
        Args:
            config: Database configuration dictionary
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        required_fields = ['host', 'port', 'database', 'username', 'password']
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False, f"Missing or empty field: {field}"
        
        # Validate port
        try:
            port = int(config['port'])
            if port < 1 or port > 65535:
                return False, "Port must be between 1 and 65535"
        except (ValueError, TypeError):
            return False, "Port must be a valid integer"
        
        # Validate host format (basic validation)
        host = config['host'].strip()
        if not host or len(host) > 255:
            return False, "Invalid host format"
        
        return True, "Configuration is valid"
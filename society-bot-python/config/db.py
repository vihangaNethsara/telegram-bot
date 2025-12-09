"""
============================================
Database Configuration - MySQL Connection Pool
============================================

This module creates and manages MySQL database connections
with connection pooling for efficient database operations.

Features:
- Connection pooling for better performance
- Async-compatible synchronous operations
- Automatic connection management
- Environment-based configuration
"""

import os
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration and connection pool manager."""
    
    _pool: Optional[pooling.MySQLConnectionPool] = None
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get database configuration from environment variables."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'society_payments_db'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': True,
            'get_warnings': True,
        }
    
    @classmethod
    def initialize_pool(cls, pool_size: int = 5) -> None:
        """
        Initialize the MySQL connection pool.
        
        Args:
            pool_size: Number of connections in the pool
        """
        if cls._pool is not None:
            logger.warning("Connection pool already initialized")
            return
        
        try:
            config = cls.get_config()
            cls._pool = pooling.MySQLConnectionPool(
                pool_name="society_payments_pool",
                pool_size=pool_size,
                pool_reset_session=True,
                **config
            )
            logger.info("✅ MySQL connection pool initialized successfully")
            logger.info(f"   Host: {config['host']}:{config['port']}")
            logger.info(f"   Database: {config['database']}")
            logger.info(f"   Pool Size: {pool_size}")
        except Error as e:
            logger.error(f"❌ Failed to initialize connection pool: {e}")
            raise
    
    @classmethod
    def get_pool(cls) -> pooling.MySQLConnectionPool:
        """Get the connection pool, initializing if necessary."""
        if cls._pool is None:
            cls.initialize_pool()
        return cls._pool
    
    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        Context manager for getting a database connection from the pool.
        
        Usage:
            with DatabaseConfig.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        connection = None
        try:
            pool = cls.get_pool()
            connection = pool.get_connection()
            yield connection
        except Error as e:
            logger.error(f"❌ Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @classmethod
    @contextmanager
    def get_cursor(cls, dictionary: bool = True):
        """
        Context manager for getting a database cursor.
        
        Args:
            dictionary: If True, returns rows as dictionaries
            
        Usage:
            with DatabaseConfig.get_cursor() as cursor:
                cursor.execute("SELECT * FROM table")
                rows = cursor.fetchall()
        """
        with cls.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary)
            try:
                yield cursor
                connection.commit()
            except Error as e:
                connection.rollback()
                logger.error(f"❌ Database error: {e}")
                raise
            finally:
                cursor.close()
    
    @classmethod
    def test_connection(cls) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful
        """
        try:
            with cls.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            logger.info("✅ Database connection test successful")
            return True
        except Error as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
    
    @classmethod
    def initialize_database(cls) -> None:
        """
        Initialize database tables.
        Creates the society_payments table if it doesn't exist.
        """
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS society_payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                member_name VARCHAR(100) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                recorded_by BIGINT NOT NULL,
                payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_member_name (member_name),
                INDEX idx_payment_date (payment_date),
                INDEX idx_recorded_by (recorded_by)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        try:
            with cls.get_cursor() as cursor:
                cursor.execute(create_table_sql)
            logger.info("✅ Database table initialized successfully")
        except Error as e:
            logger.error(f"❌ Failed to initialize database table: {e}")
            raise
    
    @classmethod
    def close_pool(cls) -> None:
        """Close all connections in the pool."""
        # Note: mysql-connector-python doesn't have explicit pool close
        # Connections are closed when they go out of scope
        cls._pool = None
        logger.info("✅ Database connection pool closed")


# Convenience functions for easy importing
def get_connection():
    """Get a database connection from the pool."""
    return DatabaseConfig.get_connection()


def get_cursor(dictionary: bool = True):
    """Get a database cursor."""
    return DatabaseConfig.get_cursor(dictionary=dictionary)


def init_db():
    """Initialize database connection pool and tables."""
    DatabaseConfig.initialize_pool()
    DatabaseConfig.test_connection()
    DatabaseConfig.initialize_database()


def close_db():
    """Close database connections."""
    DatabaseConfig.close_pool()

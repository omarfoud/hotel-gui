"""
Database Service Module

Design Patterns:
1. Singleton Pattern:
   - Single database connection instance
   - Global point of access

2. Facade Pattern:
   - Provides unified interface to database operations
   - Simplifies database interaction

3. Repository Pattern:
   - Abstracts data persistence
   - Centralizes data access logic

SOLID Principles:
1. Single Responsibility Principle (SRP):
   - DatabaseService handles only database operations
   - Each method has a single, focused purpose

2. Open/Closed Principle (OCP):
   - New database operations can be added without modifying existing code
   - Query execution is extensible

3. Interface Segregation Principle (ISP):
   - Clean interfaces for database operations
   - Methods grouped by functionality

4. Dependency Inversion Principle (DIP):
   - Depends on database abstractions
   - Implementation details isolated

5. Liskov Substitution Principle (LSP):
   - Database operations maintain consistent behavior
   - Methods follow expected contract
"""

import sqlite3
from pathlib import Path
import os
import logging
from contextlib import contextmanager
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hotel.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    # Design Pattern: Singleton
    # SOLID Principle: Single Responsibility Principle (SRP)
    # Single instance handling all database operations
    """
    _instance = None
    _connection_pool = []
    MAX_POOL_SIZE = 5
    
    def __new__(cls):
        """
        # Design Pattern: Singleton
        # SOLID Principle: Single Responsibility Principle (SRP)
        # Ensures only one instance of DatabaseService exists
        """
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._initialize_db()
        return cls._instance
    
    def _initialize_db(self):
        """
        # Design Pattern: Template Method
        # SOLID Principle: Open/Closed Principle (OCP)
        # Database initialization can be extended without modification
        """
        try:
            # Ensure the database directory exists
            db_dir = Path(os.path.expanduser("~")) / "hotel_management"
            db_dir.mkdir(exist_ok=True)
            
            self.db_path = db_dir / "hotel.db"
            logger.info(f"Initializing database at {self.db_path}")
            self._create_tables()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        # Design Pattern: Factory Method & Pool Pattern
        # SOLID Principle: Dependency Inversion Principle (DIP)
        # Manages database connections through abstraction
        """
        connection = None
        try:
            # Try to get connection from pool
            if self._connection_pool:
                connection = self._connection_pool.pop()
            else:
                connection = sqlite3.connect(
                    self.db_path,
                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
                )
                connection.row_factory = sqlite3.Row
            
            yield connection
            
            # Return connection to pool if not too many
            if len(self._connection_pool) < self.MAX_POOL_SIZE:
                self._connection_pool.append(connection)
            else:
                connection.close()
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.close()
            raise
    
    def _create_tables(self):
        """Create necessary database tables"""
        create_tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS room_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_type TEXT UNIQUE NOT NULL,
                price REAL NOT NULL,
                capacity INTEGER DEFAULT 20,
                description TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                room_type TEXT NOT NULL,
                checkin_date DATE NOT NULL,
                checkout_date DATE NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (room_type) REFERENCES room_types (room_type)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (booking_id) REFERENCES bookings (id)
            )
            """
        ]
        
        try:
            for sql in create_tables_sql:
                self.execute_query(sql)
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
        
        # Insert default room types if they don't exist
        insert_room_types_sql = """
        INSERT OR IGNORE INTO room_types (room_type, price, capacity, description)
        VALUES 
            ('Single', 100.00, 20, 'A cozy room with a single bed'),
            ('Double', 150.00, 20, 'Comfortable room with a double bed'),
            ('Suite', 250.00, 20, 'Luxury suite with separate living area'),
            ('Family', 300.00, 20, 'Spacious room for family stays')
        """
        
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(insert_room_types_sql)
                conn.commit()
            except sqlite3.Error as e:
                logger.error(f"Error inserting default room types: {e}")
                conn.rollback()
    
    def execute_query(self, query: str, params: tuple = ()):
        """
        # Design Pattern: Facade Pattern
        # SOLID Principle: Interface Segregation Principle (ISP)
        # Provides simple interface for query execution
        """
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                logger.error(f"Error executing query: {e}")
                conn.rollback()
    
    def fetch_query(self, query: str, params: tuple = ()):
        """
        # Design Pattern: Repository Pattern
        # SOLID Principle: Single Responsibility Principle (SRP)
        # Handles only data retrieval operations
        """
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
            except sqlite3.Error as e:
                logger.error(f"Error fetching query: {e}")
    
    def fetch_one(self, query: str, params: tuple = ()):
        """Fetch a single result from a database query"""
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchone()
            except sqlite3.Error as e:
                logger.error(f"Error fetching one: {e}")

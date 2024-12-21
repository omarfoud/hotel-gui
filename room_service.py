"""
Room Service Module

Design Patterns:
1. Service Pattern:
   - Encapsulates room management business logic
   - Provides high-level room operations

2. Observer Pattern:
   - Notifies UI of room status changes
   - Loose coupling between room logic and UI

3. State Pattern:
   - Manages different room states
   - Encapsulates state-specific behavior

4. Command Pattern:
   - Encapsulates room operations as commands
   - Supports operation history

SOLID Principles:
1. Single Responsibility Principle (SRP):
   - RoomService handles only room-related operations
   - Each method has a single, clear purpose

2. Open/Closed Principle (OCP):
   - New room types and operations can be added without modification
   - Room management is extensible

3. Interface Segregation Principle (ISP):
   - Clean interfaces for room operations
   - Methods grouped by functionality

4. Dependency Inversion Principle (DIP):
   - Depends on service abstractions
   - Implementation details isolated

5. Liskov Substitution Principle (LSP):
   - Room operations maintain consistent behavior
   - Methods follow expected contract
"""

from typing import List, Tuple, Dict, Any, Optional, Union
from datetime import datetime, date
from date_service import DateService
import logging

logger = logging.getLogger(__name__)

class RoomService:
    def __init__(self, database_service):
        """
        # Design Pattern: Dependency Injection
        # SOLID Principle: Dependency Inversion Principle (DIP)
        # Depends on database_service abstraction rather than concrete implementation
        """
        self.database_service = database_service
        self.date_service = DateService()
        self._init_database()
    
    def _init_database(self):
        """
        # Design Pattern: Template Method
        # SOLID Principle: Single Responsibility Principle (SRP)
        # Handles only database initialization logic
        """
        try:
            # Create room types table
            self.database_service.execute_query(
                """
                CREATE TABLE IF NOT EXISTS room_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_type TEXT UNIQUE NOT NULL,
                    price REAL NOT NULL,
                    capacity INTEGER DEFAULT 20,
                    description TEXT
                )
                """
            )
            
            # Insert default room types if table is empty
            if not self.get_room_types():
                default_rooms = [
                    ('Standard', 1000, 20, 'Comfortable room with basic amenities'),
                    ('Deluxe', 2000, 15, 'Spacious room with premium amenities'),
                    ('Suite', 3000, 10, 'Luxury suite with separate living area'),
                    ('Family', 4000, 5, 'Large room ideal for families')
                ]
                
                for room in default_rooms:
                    self.database_service.execute_query(
                        """
                        INSERT INTO room_types (room_type, price, capacity, description)
                        VALUES (?, ?, ?, ?)
                        """,
                        room
                    )
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def get_room_types(self) -> List[Tuple[str, float, int, str]]:
        """
        # Design Pattern: Repository Pattern
        # SOLID Principle: Single Responsibility Principle (SRP)
        # Handles only room type data retrieval
        """
        try:
            result = self.database_service.fetch_query(
                "SELECT room_type, price, capacity, description FROM room_types"
            )
            return result if result else []
        except Exception as e:
            logger.error(f"Error fetching room types: {str(e)}")
            return []
    
    def get_room_price(self, room_type: str) -> float:
        """
        # Design Pattern: Service Pattern
        # SOLID Principle: Open/Closed Principle (OCP)
        # New pricing strategies can be added without modifying this method
        """
        try:
            result = self.database_service.fetch_query(
                "SELECT price FROM room_types WHERE room_type = ?",
                (room_type,)
            )
            if not result or not result[0]:
                logger.error(f"No price found for room type: {room_type}")
                raise ValueError(f"Invalid room type: {room_type}")
            return float(result[0][0])
        except Exception as e:
            logger.error(f"Error fetching room price: {str(e)}")
            raise
    
    def get_room_capacity(self, room_type: str) -> int:
        """
        # Design Pattern: Service Pattern
        # SOLID Principle: Interface Segregation Principle (ISP)
        # Provides specific interface for capacity queries
        """
        try:
            result = self.database_service.fetch_query(
                "SELECT capacity FROM room_types WHERE room_type = ?",
                (room_type,)
            )
            if not result or not result[0]:
                logger.error(f"No capacity found for room type: {room_type}")
                raise ValueError(f"Invalid room type: {room_type}")
            return int(result[0][0])
        except Exception as e:
            logger.error(f"Error fetching room capacity: {str(e)}")
            raise
    
    def is_room_available(self, room_type: str, checkin_date: Union[datetime, date], checkout_date: Union[datetime, date]) -> bool:
        """
        # Design Pattern: Strategy Pattern
        # SOLID Principle: Single Responsibility Principle (SRP)
        # Handles only room availability logic
        """
        try:
            # Convert dates to strings for database query
            checkin_str = self.date_service.to_string(checkin_date)
            checkout_str = self.date_service.to_string(checkout_date)
            
            valid, error_msg = self.date_service.validate_dates(checkin_date, checkout_date)
            if not valid:
                logger.error(f"Date validation failed: {error_msg}")
                return False
            
            # Get room capacity
            capacity = self.get_room_capacity(room_type)
            
            # Get number of active bookings for these dates
            overlapping_bookings = self.database_service.fetch_query(
                """
                SELECT COUNT(*) as booking_count
                FROM bookings
                WHERE room_type = ?
                AND status = 'active'
                AND (
                    (date(checkin_date) <= date(?) AND date(checkout_date) > date(?))  -- Booking starts before checkin and ends after checkin
                    OR (date(checkin_date) < date(?) AND date(checkout_date) >= date(?))  -- Booking starts before checkout and ends after checkout
                    OR (date(checkin_date) >= date(?) AND date(checkout_date) <= date(?))  -- Booking is completely within the requested period
                )
                """,
                (room_type, checkin_str, checkin_str, checkout_str, checkout_str, checkin_str, checkout_str)
            )
            
            if not overlapping_bookings:
                logger.error("Failed to fetch overlapping bookings")
                return False
            
            current_bookings = int(overlapping_bookings[0][0])
            logger.info(f"Found {current_bookings} overlapping bookings for {room_type} between {checkin_str} and {checkout_str}")
            
            # Room is available if number of current bookings is less than capacity
            is_available = current_bookings < capacity
            if not is_available:
                logger.info(f"Room {room_type} is fully booked ({current_bookings}/{capacity})")
            
            return is_available
            
        except Exception as e:
            logger.error(f"Error checking room availability: {str(e)}")
            return False
    
    def calculate_total_bill(self, room_type: str, checkin_date: date, checkout_date: date) -> Dict[str, float]:
        """Calculate total bill for a booking"""
        try:
            # Get room price
            price_per_night = self.get_room_price(room_type)
            
            # Calculate number of nights
            nights = (checkout_date - checkin_date).days
            
            # Calculate charges
            room_charge = price_per_night * nights
            tax = room_charge * 0.18  # 18% tax
            service_charge = room_charge * 0.10  # 10% service charge
            total = room_charge + tax + service_charge
            
            return {
                'price_per_night': price_per_night,
                'nights': nights,
                'room_charge': room_charge,
                'tax': tax,
                'service_charge': service_charge,
                'total': total
            }
        except Exception as e:
            logger.error(f"Error calculating bill: {str(e)}")
            raise

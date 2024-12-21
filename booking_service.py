"""
Booking Service Module

Design Patterns:
1. Observer Pattern:
   - Notifies UI of booking status changes
   - Loose coupling between booking logic and UI

2. Strategy Pattern:
   - Different booking validation strategies
   - Flexible booking rules implementation

3. Template Method Pattern:
   - Defines skeleton of booking process
   - Subclasses can customize specific steps

4. Command Pattern:
   - Encapsulates booking requests
   - Supports undo/redo operations

SOLID Principles:
1. Single Responsibility Principle (SRP):
   - BookingService handles only booking operations
   - Each method has a single, focused purpose

2. Open/Closed Principle (OCP):
   - New booking types can be added without modifying existing code
   - Validation strategies can be extended

3. Interface Segregation Principle (ISP):
   - Clean interfaces for different booking operations
   - Observers implement only needed methods

4. Dependency Inversion Principle (DIP):
   - Depends on service abstractions
   - Implementation details are isolated

5. Liskov Substitution Principle (LSP):
   - Booking types are interchangeable
   - Maintains consistent behavior
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from date_service import DateService

# Observer Pattern
class BookingObserver(ABC):
    @abstractmethod
    def on_booking_success(self, booking_data: Dict[str, Any]):
        pass

    @abstractmethod
    def on_booking_error(self, error_message: str):
        pass

# Strategy Pattern - Validation Strategies
class BookingValidationStrategy(ABC):
    @abstractmethod
    def validate(self, booking_data: Dict[str, Any]) -> Tuple[bool, str]:
        pass

class RequiredFieldsValidation(BookingValidationStrategy):
    def validate(self, booking_data: Dict[str, Any]) -> Tuple[bool, str]:
        required_fields = {
            'name': 'Name',
            'phone': 'Phone Number',
            'address': 'Address',
            'room_type': 'Room Type'
        }
        
        for field, label in required_fields.items():
            if not booking_data.get(field):
                return False, f"{label} is required!"
                
        if booking_data['room_type'] == "Select Room Type":
            return False, "Please select a room type!"
            
        return True, ""

class DateValidation(BookingValidationStrategy):
    def validate(self, booking_data: Dict[str, Any]) -> Tuple[bool, str]:
        checkin = booking_data.get('checkin_date')
        checkout = booking_data.get('checkout_date')
        
        if not checkin or not checkout:
            return False, "Check-in and Check-out dates are required!"
            
        # DateEntry widget returns date objects directly
        if checkout <= checkin:
            return False, "Check-out date must be after check-in date!"
            
        return True, ""

# Strategy Pattern - Booking Process Strategies
class BookingProcessStrategy(ABC):
    @abstractmethod
    def process(self, booking_data: Dict[str, Any], database_service: Any) -> Tuple[bool, str, Any]:
        pass

class StandardBookingProcess(BookingProcessStrategy):
    def process(self, booking_data: Dict[str, Any], database_service: Any) -> Tuple[bool, str, Any]:
        try:
            # Save customer data
            database_service.execute_query(
                "INSERT INTO Customers (name, phone, address) VALUES (?, ?, ?)",
                (booking_data['name'], booking_data['phone'], booking_data['address'])
            )
            
            # Get customer ID
            customer_id = database_service.fetch_query(
                "SELECT id FROM Customers WHERE name=? AND phone=?",
                (booking_data['name'], booking_data['phone'])
            )[0][0]
            
            # Convert dates to strings - the DateEntry widget returns a datetime.date object
            checkin_str = booking_data['checkin_date'].strftime('%Y-%m-%d')
            checkout_str = booking_data['checkout_date'].strftime('%Y-%m-%d')
            
            # Save booking data
            database_service.execute_query(
                "INSERT INTO Bookings (customer_id, room_type, checkin_date, checkout_date) VALUES (?, ?, ?, ?)",
                (
                    customer_id,
                    booking_data['room_type'],
                    checkin_str,
                    checkout_str
                )
            )
            
            return True, "Booking has been successfully saved!", customer_id
            
        except Exception as e:
            return False, f"An error occurred: {str(e)}", None

# Booking Service
class BookingService:
    """Service for managing bookings"""
    
    def __init__(self, database_service, room_service):
        self.database_service = database_service
        self.room_service = room_service
        self.date_service = DateService()
        self.observers: List[BookingObserver] = []
        self.validation_strategies: List[BookingValidationStrategy] = [
            RequiredFieldsValidation(),
            DateValidation()
        ]
        self.booking_strategy: BookingProcessStrategy = StandardBookingProcess()
    
    def attach(self, observer: BookingObserver):
        """Attach an observer"""
        self.observers.append(observer)
    
    def detach(self, observer: BookingObserver):
        """Detach an observer"""
        self.observers.remove(observer)
    
    def notify_success(self, booking_data: Dict[str, Any]):
        """Notify observers of successful booking"""
        for observer in self.observers:
            observer.on_booking_success(booking_data)
    
    def notify_error(self, error_message: str):
        """Notify observers of booking error"""
        for observer in self.observers:
            observer.on_booking_error(error_message)
    
    def set_booking_strategy(self, strategy: BookingProcessStrategy):
        self.booking_strategy = strategy
    
    def add_validation_strategy(self, strategy: BookingValidationStrategy):
        self.validation_strategies.append(strategy)
    
    def validate_booking_data(self, booking_data: Dict[str, Any]) -> Optional[str]:
        """Validate booking data"""
        required_fields = ['name', 'phone', 'address', 'room_type', 'checkin_date', 'checkout_date']
        
        # Check required fields
        for field in required_fields:
            if field not in booking_data or not booking_data[field]:
                return f"{field.replace('_', ' ').title()} is required"
        
        # Validate dates
        is_valid_dates, message = self.date_service.validate_dates(
            booking_data['checkin_date'],
            booking_data['checkout_date']
        )
        if not is_valid_dates:
            return message
        
        return None
    
    def process_booking(self, booking_data: Dict[str, Any]):
        """Process a new booking"""
        try:
            # Validate booking data
            error = self.validate_booking_data(booking_data)
            if error:
                self.notify_error(error)
                return
            
            # Run all validation strategies
            for validator in self.validation_strategies:
                is_valid, message = validator.validate(booking_data)
                if not is_valid:
                    self.notify_error(message)
                    return
            
            # Check room availability
            if not self.room_service.is_room_available(
                booking_data['room_type'],
                booking_data['checkin_date'],
                booking_data['checkout_date']
            ):
                self.notify_error("Selected room is not available for these dates!")
                return
            
            # Insert customer
            customer_id = self.database_service.execute_query(
                """
                INSERT INTO customers (name, phone, address)
                VALUES (?, ?, ?)
                """,
                (booking_data['name'], booking_data['phone'], booking_data['address'])
            )
            
            # Format dates for database
            checkin_str = self.date_service.to_string(booking_data['checkin_date'])
            checkout_str = self.date_service.to_string(booking_data['checkout_date'])
            
            # Insert booking
            booking_id = self.database_service.execute_query(
                """
                INSERT INTO bookings (customer_id, room_type, checkin_date, checkout_date, status)
                VALUES (?, ?, ?, ?, 'active')
                """,
                (customer_id, booking_data['room_type'], checkin_str, checkout_str)
            )
            
            # Calculate bill
            bill_info = self.room_service.calculate_total_bill(
                booking_data['room_type'],
                booking_data['checkin_date'],
                booking_data['checkout_date']
            )
            
            # Insert payment record
            self.database_service.execute_query(
                """
                INSERT INTO payments (booking_id, amount, payment_method, status)
                VALUES (?, ?, 'pending', 'pending')
                """,
                (booking_id, bill_info['total'])
            )
            
            # Notify success
            self.notify_success(booking_data)
            
        except Exception as e:
            self.notify_error(f"An error occurred: {str(e)}")

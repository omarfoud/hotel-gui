"""
Date Service Module

Design Patterns:
1. Strategy Pattern:
   - Different strategies for date validation
   - Flexible date handling approaches

2. Facade Pattern:
   - Provides simplified interface for date operations
   - Hides complexity of date handling

SOLID Principles:
1. Single Responsibility Principle (SRP):
   - DateService handles only date-related operations
   - Each method has a single, focused purpose

2. Open/Closed Principle (OCP):
   - New date formats can be added without modifying existing code
   - Validation rules can be extended

3. Interface Segregation Principle (ISP):
   - Methods are specific to date operations
   - Clean, focused interface

4. Dependency Inversion Principle (DIP):
   - Depends on datetime abstractions
   - Implementation details are isolated

Handles all date-related operations consistently throughout the application.
"""

from datetime import datetime, date, timedelta
from typing import Union, Tuple

class DateService:
    """Service for handling date operations consistently"""
    
    DATE_FORMAT = '%Y-%m-%d'
    
    @staticmethod
    def to_string(date_obj: Union[datetime, date]) -> str:
        """Convert a date or datetime object to string format"""
        if isinstance(date_obj, (datetime, date)):
            return date_obj.strftime(DateService.DATE_FORMAT)
        raise ValueError(f"Expected datetime.date or datetime.datetime, got {type(date_obj)}")
    
    @staticmethod
    def parse_date(date_str: str) -> date:
        """Parse a date string into a date object"""
        try:
            return datetime.strptime(date_str, DateService.DATE_FORMAT).date()
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD, got: {date_str}")
    
    @staticmethod
    def validate_dates(checkin: Union[datetime, date], checkout: Union[datetime, date]) -> Tuple[bool, str]:
        """Validate check-in and check-out dates"""
        try:
            # Convert to date objects if datetime
            checkin_date = checkin.date() if isinstance(checkin, datetime) else checkin
            checkout_date = checkout.date() if isinstance(checkout, datetime) else checkout
            
            # Get today's date
            today = date.today()
            
            # Check if dates are in the past
            if checkin_date < today:
                return False, "Check-in date cannot be in the past"
            
            # Check if checkout is before checkin
            if checkout_date <= checkin_date:
                return False, "Check-out date must be after check-in date"
            
            # Check if stay is too long (e.g., more than 30 days)
            if (checkout_date - checkin_date).days > 30:
                return False, "Maximum stay is 30 days"
            
            return True, ""
            
        except Exception as e:
            return False, f"Date validation error: {str(e)}"

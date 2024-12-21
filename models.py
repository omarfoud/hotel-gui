from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Customer:
    """Customer data model"""
    name: str
    phone: str
    address: str
    id: Optional[int] = None

    @classmethod
    def from_db(cls, data: tuple):
        """Create Customer instance from database tuple"""
        id_, name, phone, address = data
        return cls(name=name, phone=phone, address=address, id=id_)

@dataclass
class Booking:
    """Booking data model"""
    customer_id: int
    room_type: str
    checkin_date: datetime
    checkout_date: datetime
    id: Optional[int] = None
    status: Optional[str] = None

    @classmethod
    def from_db(cls, data: tuple):
        """Create Booking instance from database tuple"""
        id_, customer_id, room_type, checkin, checkout = data
        return cls(
            id=id_,
            customer_id=customer_id,
            room_type=room_type,
            checkin_date=datetime.strptime(checkin, '%Y-%m-%d'),
            checkout_date=datetime.strptime(checkout, '%Y-%m-%d')
        )

    @property
    def duration(self) -> int:
        """Calculate booking duration in days"""
        return (self.checkout_date - self.checkin_date).days

@dataclass
class Room:
    """Room data model"""
    room_type: str
    price: float
    capacity: int = 20
    current_bookings: int = 0

    @property
    def is_available(self) -> bool:
        """Check if room is available"""
        return self.current_bookings < self.capacity

@dataclass
class Payment:
    """Payment data model"""
    amount: float
    method: str
    customer_id: Optional[int] = None
    status: str = "Pending"
    id: Optional[int] = None

    @classmethod
    def from_db(cls, data: tuple):
        """Create Payment instance from database tuple"""
        id_, customer_id, amount, method, status = data
        return cls(
            id=id_,
            customer_id=customer_id,
            amount=amount,
            method=method,
            status=status
        )

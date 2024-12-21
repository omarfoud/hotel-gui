from abc import ABC, abstractmethod
from typing import List, Tuple, Any
from datetime import datetime

# Observer Pattern - Interface for observers
class RecordsObserver(ABC):
    @abstractmethod
    def update(self, records: List[Tuple]):
        pass

# Strategy Pattern - Interface for different record loading strategies
class RecordLoadStrategy(ABC):
    @abstractmethod
    def load(self, database_service) -> List[Tuple]:
        pass

# Concrete Strategies
class AllRecordsStrategy(RecordLoadStrategy):
    def load(self, database_service) -> List[Tuple]:
        return database_service.fetch_query("""
            SELECT 
                b.id, 
                c.name, 
                b.room_type, 
                b.checkin_date, 
                b.checkout_date,
                julianday(b.checkout_date) - julianday(b.checkin_date) as nights,
                rt.price as price_per_night,
                (julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price as room_charge,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 0.18 as tax,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 0.10 as service_charge,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 1.28 as total,
                b.status
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN room_types rt ON b.room_type = rt.room_type
            ORDER BY b.checkin_date DESC
        """)

class ActiveRecordsStrategy(RecordLoadStrategy):
    def load(self, database_service) -> List[Tuple]:
        return database_service.fetch_query("""
            SELECT 
                b.id, 
                c.name, 
                b.room_type, 
                b.checkin_date, 
                b.checkout_date,
                julianday(b.checkout_date) - julianday(b.checkin_date) as nights,
                rt.price as price_per_night,
                (julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price as room_charge,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 0.18 as tax,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 0.10 as service_charge,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 1.28 as total,
                'Active' as status
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN room_types rt ON b.room_type = rt.room_type
            WHERE b.status = 'active'
            AND date('now') BETWEEN b.checkin_date AND b.checkout_date
            ORDER BY b.checkin_date DESC
        """)

class UpcomingRecordsStrategy(RecordLoadStrategy):
    def load(self, database_service) -> List[Tuple]:
        return database_service.fetch_query("""
            SELECT 
                b.id, 
                c.name, 
                b.room_type, 
                b.checkin_date, 
                b.checkout_date,
                julianday(b.checkout_date) - julianday(b.checkin_date) as nights,
                rt.price as price_per_night,
                (julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price as room_charge,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 0.18 as tax,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 0.10 as service_charge,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 1.28 as total,
                'Upcoming' as status
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN room_types rt ON b.room_type = rt.room_type
            WHERE b.status = 'active'
            AND date('now') < b.checkin_date
            ORDER BY b.checkin_date DESC
        """)

class CompletedRecordsStrategy(RecordLoadStrategy):
    def load(self, database_service) -> List[Tuple]:
        return database_service.fetch_query("""
            SELECT 
                b.id, 
                c.name, 
                b.room_type, 
                b.checkin_date, 
                b.checkout_date,
                julianday(b.checkout_date) - julianday(b.checkin_date) as nights,
                rt.price as price_per_night,
                (julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price as room_charge,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 0.18 as tax,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 0.10 as service_charge,
                ((julianday(b.checkout_date) - julianday(b.checkin_date)) * rt.price) * 1.28 as total,
                'Completed' as status
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN room_types rt ON b.room_type = rt.room_type
            WHERE b.status = 'active'
            AND date('now') > b.checkout_date
            ORDER BY b.checkin_date DESC
        """)

# Records Service implementing Observer pattern
class RecordsService:
    def __init__(self, database_service):
        self.database_service = database_service
        self.observers = []
        self.strategy = AllRecordsStrategy()
    
    def attach(self, observer: RecordsObserver):
        self.observers.append(observer)
    
    def detach(self, observer: RecordsObserver):
        self.observers.remove(observer)
    
    def notify(self, records: List[Tuple]):
        for observer in self.observers:
            observer.update(records)
    
    def set_strategy(self, strategy: RecordLoadStrategy):
        self.strategy = strategy
        self.load_records()
    
    def load_records(self):
        try:
            records = self.strategy.load(self.database_service)
            self.notify(records if records else [])
        except Exception as e:
            print(f"Error loading records: {str(e)}")
            self.notify([])

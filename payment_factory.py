"""
Payment Factory Module

Design Patterns:
1. Factory Pattern:
   - Creates different payment processors
   - Encapsulates payment processor creation logic

2. Strategy Pattern:
   - Different payment strategies for different methods
   - Flexible payment processing implementation

3. Template Method Pattern:
   - Defines skeleton of payment processing
   - Subclasses customize specific steps

4. Bridge Pattern:
   - Separates payment abstraction from implementation
   - Allows both to vary independently

SOLID Principles:
1. Single Responsibility Principle (SRP):
   - Each payment processor handles one payment method
   - Factory only handles processor creation

2. Open/Closed Principle (OCP):
   - New payment methods can be added without modifying existing code
   - Payment processors are extensible

3. Interface Segregation Principle (ISP):
   - Clean interfaces for payment processing
   - Processors implement only needed methods

4. Dependency Inversion Principle (DIP):
   - Depends on processor abstractions
   - Implementation details are isolated

5. Liskov Substitution Principle (LSP):
   - Payment processors are interchangeable
   - Maintains consistent behavior
"""

from abc import ABC, abstractmethod
from tkinter import messagebox
from typing import Dict

class PaymentProcessor(ABC):
    """Abstract base class for payment processing"""
    
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        """Process the payment and return success status"""
        pass
    
    @abstractmethod
    def get_payment_fields(self) -> Dict[str, str]:
        """Return the fields required for this payment method"""
        pass

class CreditCardProcessor(PaymentProcessor):
    """Credit card payment processor"""
    
    def process_payment(self, amount: float) -> bool:
        # In a real application, this would integrate with a payment gateway
        return True
    
    def get_payment_fields(self) -> Dict[str, str]:
        return {
            'card_number': 'Card Number',
            'expiry_date': 'MM/YY',
            'cvv': 'CVV'
        }

class DebitCardProcessor(PaymentProcessor):
    """Debit card payment processor"""
    
    def process_payment(self, amount: float) -> bool:
        return True
    
    def get_payment_fields(self) -> Dict[str, str]:
        return {
            'card_number': 'Card Number',
            'expiry_date': 'MM/YY',
            'cvv': 'CVV',
            'bank_name': 'Bank Name'
        }

class CashProcessor(PaymentProcessor):
    """Cash payment processor"""
    
    def process_payment(self, amount: float) -> bool:
        return True
    
    def get_payment_fields(self) -> Dict[str, str]:
        return {
            'amount_tendered': 'Amount Tendered'
        }

class UPIProcessor(PaymentProcessor):
    """UPI payment processor"""
    
    def process_payment(self, amount: float) -> bool:
        return True
    
    def get_payment_fields(self) -> Dict[str, str]:
        return {
            'upi_id': 'UPI ID'
        }

class PaymentFactory:
    """Factory class for creating payment processors"""
    
    @staticmethod
    def get_payment_processor(payment_method: str) -> PaymentProcessor:
        """Create and return a payment processor based on the payment method"""
        processors = {
            'Credit Card': CreditCardProcessor(),
            'Debit Card': DebitCardProcessor(),
            'Cash': CashProcessor(),
            'UPI': UPIProcessor()
        }
        
        if payment_method not in processors:
            raise ValueError(f"Unsupported payment method: {payment_method}")
        
        return processors[payment_method]
    
    @staticmethod
    def get_available_methods() -> list:
        """Return list of available payment methods"""
        return ['Credit Card', 'Debit Card', 'Cash', 'UPI']
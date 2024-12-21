"""
Hotel Management System - Main Application
Design Patterns and SOLID Principles:

1. Observer Pattern:
   - BookingWindow observes BookingService for booking updates
   - RecordsWindow observes RecordsService for record updates

2. Template Method Pattern:
   - BaseWindow defines the template for window creation
   - BaseFormWindow and BaseTableWindow extend it with specific implementations

3. Single Responsibility Principle (SRP):
   - Each window class has a single responsibility
   - HotelManagementApp manages main window
   - BookingWindow handles bookings
   - RecordsWindow handles records display

4. Open/Closed Principle (OCP):
   - Window classes can be extended without modification
   - New features can be added by creating new window classes

5. Interface Segregation Principle (ISP):
   - Windows implement only the interfaces they need
   - BookingObserver for booking windows
   - RecordsObserver for records windows

6. Dependency Inversion Principle (DIP):
   - High-level modules depend on abstractions
   - Windows depend on service interfaces, not concrete implementations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database_service import DatabaseService
from payment_factory import PaymentFactory
from room_service import RoomService
from records_service import (
    RecordsService, RecordsObserver,
    AllRecordsStrategy, ActiveRecordsStrategy,
    UpcomingRecordsStrategy, CompletedRecordsStrategy
)
from booking_service import BookingService, BookingObserver
from base_window import BaseWindow, BaseFormWindow, BaseTableWindow, DataServiceMixin
from models import Customer, Booking, Room, Payment
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class HotelManagementApp(tk.Tk):
    """Main application window"""
    
    def __init__(self, database_service, room_service):
        super().__init__()
        
        # Set up error handling
        self.report_callback_exception = self.show_error
        
        self.database_service = database_service
        self.room_service = room_service
        self._init_window()
        self._init_styles()
        self._create_widgets()
    
    def show_error(self, exc, val, tb):
        """Global error handler"""
        error_message = f"An error occurred:\n{str(val)}"
        messagebox.showerror("Error", error_message)
        logging.error("Exception:", exc_info=(exc, val, tb))
    
    def _init_window(self):
        """Initialize main window"""
        self.title("Hotel Management System")
        self.geometry("1024x768")
        self.configure(bg='#f0f0f0')
        
        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1024) // 2
        y = (screen_height - 768) // 2
        self.geometry(f"1024x768+{x}+{y}")
        
        # Make window responsive
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
    def _init_styles(self):
        """Initialize ttk styles with a modern look"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        primary_color = "#2196F3"
        secondary_color = "#f0f0f0"
        text_color = "#333333"
        
        # Button style
        self.style.configure(
            'Custom.TButton',
            padding=10,
            relief="flat",
            background=primary_color,
            foreground="white",
            font=('Arial', 11),
            borderwidth=0
        )
        self.style.map(
            'Custom.TButton',
            background=[('active', '#1976D2'), ('disabled', '#BDBDBD')],
            foreground=[('disabled', '#757575')]
        )
        
        # Label styles
        self.style.configure(
            'Custom.TLabel',
            background=secondary_color,
            foreground=text_color,
            font=('Arial', 11)
        )
        self.style.configure(
            'Header.TLabel',
            background=secondary_color,
            foreground=text_color,
            font=('Arial', 28, 'bold')
        )
        
        # Frame style
        self.style.configure(
            'Custom.TFrame',
            background=secondary_color
        )
    
    def _create_widgets(self):
        """Create main window widgets"""
        main_container = ttk.Frame(self, style='Custom.TFrame')
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        self._create_header(main_container)
        self._create_main_menu(main_container)
    
    def _create_header(self, container):
        """Create header section"""
        header_frame = ttk.Frame(container, style='Custom.TFrame')
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        # Logo and title
        ttk.Label(
            header_frame,
            text="Hotel Management System",
            style='Header.TLabel'
        ).grid(row=0, column=0, sticky="w")
        
        # Current time display
        self.time_label = ttk.Label(
            header_frame,
            text="",
            style='Custom.TLabel'
        )
        self.time_label.grid(row=0, column=1, sticky="e")
        self._update_time()
    
    def _update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.configure(text=current_time)
        self.after(1000, self._update_time)
    
    def _create_main_menu(self, container):
        """Create main menu with modern card-style buttons"""
        menu_frame = ttk.Frame(container, style='Custom.TFrame')
        menu_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure grid with 3 columns
        for i in range(3):
            menu_frame.grid_columnconfigure(i, weight=1)
        
        buttons = [
            ("Booking", "📅", self.open_booking),
            ("Rooms Info", "🏠", self.show_rooms_info),
            ("Room Service", "🍽️", self.open_restaurant_menu),
            ("Payment", "💳", self.open_payment),
            ("Records", "📊", self.show_records),
            ("Exit", "🚪", self.destroy)
        ]
        
        for idx, (text, icon, command) in enumerate(buttons):
            row, col = divmod(idx, 3)
            self._create_menu_card(menu_frame, icon, text, command, row, col)
    
    def _create_menu_card(self, parent, icon, text, command, row, col):
        """Create a card-style button for the main menu"""
        card = ttk.Frame(parent, style='Custom.TFrame')
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Icon
        ttk.Label(
            card,
            text=icon,
            style='Custom.TLabel',
            font=('Arial', 32)
        ).pack(pady=(20, 10))
        
        # Text
        ttk.Label(
            card,
            text=text,
            style='Custom.TLabel',
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 20))
        
        # Make the entire card clickable
        for child in card.winfo_children():
            child.bind('<Button-1>', lambda e, cmd=command: cmd())
        card.bind('<Button-1>', lambda e, cmd=command: cmd())
    
    def open_booking(self):
        BookingWindow(self, self.database_service)
    
    def show_rooms_info(self):
        RoomsInfoWindow(self)
    
    def open_restaurant_menu(self):
        RestaurantMenuWindow(self)
    
    def open_payment(self):
        PaymentWindow(self, self.database_service)
    
    def show_records(self):
        RecordsWindow(self, self.database_service)

class BookingWindow(BaseFormWindow, DataServiceMixin, BookingObserver):
    """Window for creating new bookings"""
    
    def __init__(self, root, database_service):
        DataServiceMixin.__init__(self, database_service)
        self.root = root  # Store root reference for records refresh
        self.room_service = root.room_service
        self.booking_service = BookingService(database_service, self.room_service)
        self.booking_service.attach(self)
        BaseFormWindow.__init__(self, root, "New Booking", "600x500")
    
    def _create_widgets(self):
        """Create booking form widgets"""
        self.show_header("New Booking")
        
        # Form fields
        fields = [
            ("Name:", "name"),
            ("Phone No.:", "phone"),
            ("Address:", "address")
        ]
        
        for idx, (label, field) in enumerate(fields, start=1):
            self.add_form_field(label, field, idx)
        
        # Room selection
        ttk.Label(self.main_frame, text="Room Type:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.room_type = self.create_combobox(
            [room[0] for room in self.room_service.get_room_types()],
            4, 1
        )
        self.room_type.set("Select Room Type")
        
        # Date selection
        ttk.Label(self.main_frame, text="Check-in Date:").grid(row=5, column=0, padx=5, pady=5, sticky='e')
        self.checkin_date = DateEntry(
            self.main_frame,
            width=37,
            background='darkblue',
            foreground='white',
            date_pattern='yyyy-mm-dd'
        )
        self.checkin_date.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(self.main_frame, text="Check-out Date:").grid(row=6, column=0, padx=5, pady=5, sticky='e')
        self.checkout_date = DateEntry(
            self.main_frame,
            width=37,
            background='darkblue',
            foreground='white',
            date_pattern='yyyy-mm-dd'
        )
        self.checkout_date.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        
        # Submit button
        self.create_button("Submit Booking", self.book_room, 7, 0)
    
    def book_room(self):
        """Process booking submission"""
        # Get form data
        form_data = self.get_form_data()
        
        # Get dates from DateEntry widgets
        checkin_date = self.checkin_date.get_date()
        checkout_date = self.checkout_date.get_date()
        
        # Prepare booking data
        booking_data = {
            **form_data,
            'room_type': self.room_type.get(),
            'checkin_date': checkin_date,
            'checkout_date': checkout_date
        }
        
        # Process booking
        self.booking_service.process_booking(booking_data)
    
    def on_booking_success(self, booking_data):
        """Handle successful booking"""
        messagebox.showinfo("Success", "Booking has been successfully saved!")
        
        # Refresh records if records window is open
        for widget in self.root.winfo_children():
            if isinstance(widget, RecordsWindow):
                widget.load_records()
        
        # Close booking window
        self.destroy()
    
    def on_booking_error(self, error_message):
        """Handle booking error"""
        messagebox.showerror("Error", error_message)
    
    def destroy(self):
        """Clean up before destroying window"""
        self.booking_service.detach(self)
        super().destroy()

class RecordsWindow(BaseTableWindow, DataServiceMixin, RecordsObserver):
    """Window for displaying booking records"""
    
    def __init__(self, root, database_service):
        DataServiceMixin.__init__(self, database_service)
        self.records_service = RecordsService(database_service)
        self.records_service.attach(self)
        self.room_service = root.room_service
        
        columns = (
            'ID', 'Customer', 'Room Type', 'Check-in', 'Check-out',
            'Nights', 'Price/Night', 'Room Charge', 'Tax', 'Service Charge', 'Total', 'Status'
        )
        BaseTableWindow.__init__(self, root, "Booking Records", columns, "1200x600")
        
        self._create_filter_buttons()
        self.records_service.load_records()
    
    def _create_filter_buttons(self):
        """Create filter buttons"""
        filters = [
            ("All Records", "all"),
            ("Active Bookings", "active"),
            ("Upcoming Bookings", "upcoming"),
            ("Completed", "completed")
        ]
        
        for idx, (text, filter_type) in enumerate(filters):
            ttk.Button(
                self.button_frame,
                text=text,
                command=lambda ft=filter_type: self.change_filter(ft)
            ).grid(row=0, column=idx, padx=5)
        
        # Add total display label
        self.total_label = ttk.Label(self.button_frame, text="Total Revenue: $0.00")
        self.total_label.grid(row=0, column=len(filters), padx=20)
    
    def change_filter(self, filter_type: str):
        """Change records filter"""
        if filter_type == "all":
            self.records_service.set_strategy(AllRecordsStrategy())
        elif filter_type == "active":
            self.records_service.set_strategy(ActiveRecordsStrategy())
        elif filter_type == "upcoming":
            self.records_service.set_strategy(UpcomingRecordsStrategy())
        elif filter_type == "completed":
            self.records_service.set_strategy(CompletedRecordsStrategy())
        
        self.records_service.load_records()
    
    def update(self, records):
        """Update table with new records"""
        self.clear_table()
        total_revenue = 0.0
        
        for record in records:
            booking_id, customer, room_type, checkin, checkout, nights, price_per_night, room_charge, tax, service_charge, total, status = record
            
            # Format dates for display
            checkin_str = checkin if isinstance(checkin, str) else checkin.strftime('%Y-%m-%d')
            checkout_str = checkout if isinstance(checkout, str) else checkout.strftime('%Y-%m-%d')
            
            # Add row with billing information
            self.add_row((
                booking_id, customer, room_type,
                checkin_str, checkout_str,
                f"{nights:.1f}", f"${price_per_night:.2f}",
                f"${room_charge:.2f}", f"${tax:.2f}",
                f"${service_charge:.2f}", f"${total:.2f}",
                status
            ))
            
            total_revenue += total
        
        # Update total revenue display
        self.total_label.config(text=f"Total Revenue: ${total_revenue:.2f}")
    
    def destroy(self):
        self.records_service.detach(self)
        super().destroy()

class PaymentWindow(tk.Toplevel):
    def __init__(self, root, database_service):
        super().__init__(root)
        self.database_service = database_service
        self.payment_factory = PaymentFactory()
        self.title("Payment")
        self.geometry("500x600")
        self.configure(bg='#f0f0f0')
        
        # Create main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Header
        ttk.Label(
            self.main_frame,
            text="Payment",
            style='Header.TLabel'
        ).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Amount field
        ttk.Label(self.main_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.amount_entry = ttk.Entry(self.main_frame, width=40)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Payment method selection
        ttk.Label(self.main_frame, text="Payment Method:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.payment_method = ttk.Combobox(
            self.main_frame,
            values=self.payment_factory.get_available_methods(),
            width=37,
            state='readonly'
        )
        self.payment_method.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.payment_method.bind('<<ComboboxSelected>>', self.on_payment_method_change)
        
        # Dynamic fields frame
        self.fields_frame = ttk.Frame(self.main_frame)
        self.fields_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Submit button
        self.submit_btn = ttk.Button(
            self.main_frame,
            text="Process Payment",
            command=self.process_payment
        )
        self.submit_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Initialize with empty fields
        self.payment_fields = {}
    
    def on_payment_method_change(self, event=None):
        """Update form fields when payment method changes"""
        # Clear existing fields
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.payment_fields = {}
        
        # Get selected payment method
        method = self.payment_method.get()
        if not method:
            return
        
        # Get processor and its required fields
        processor = self.payment_factory.get_payment_processor(method)
        required_fields = processor.get_payment_fields()
        
        # Create fields
        for i, (field_id, label) in enumerate(required_fields.items()):
            ttk.Label(self.fields_frame, text=label + ":").grid(
                row=i, column=0, padx=5, pady=5, sticky='e'
            )
            entry = ttk.Entry(self.fields_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            self.payment_fields[field_id] = entry
    
    def process_payment(self):
        """Process the payment"""
        try:
            # Validate amount
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
            
            # Get payment method
            method = self.payment_method.get()
            if not method:
                messagebox.showerror("Error", "Please select a payment method")
                return
            
            # Get processor
            processor = self.payment_factory.get_payment_processor(method)
            
            # Validate fields
            field_values = {}
            for field_id, entry in self.payment_fields.items():
                value = entry.get().strip()
                if not value:
                    messagebox.showerror("Error", f"Please fill in all fields")
                    return
                field_values[field_id] = value
            
            # Process payment
            if processor.process_payment(amount):
                messagebox.showinfo("Success", "Payment processed successfully!")
                self.destroy()
            else:
                messagebox.showerror("Error", "Payment processing failed")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

class RoomsInfoWindow(BaseWindow):
    """Window for displaying room information"""
    
    def __init__(self, root):
        self.room_service = root.room_service
        super().__init__(root, "Room Information", "800x600")
    
    def _create_widgets(self):
        """Create widgets for room information display"""
        self.show_header("Available Room Types")
        
        # Create frame for room cards
        cards_frame = ttk.Frame(self.main_frame)
        cards_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        
        # Configure grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(0, weight=1)
        
        # Get room information
        room_info = self.room_service.get_room_types()
        
        # Create a card for each room type
        for idx, (room_type, price, capacity, description) in enumerate(room_info):
            # Create card frame
            card = ttk.Frame(cards_frame, style='Card.TFrame')
            card.grid(row=idx, column=0, sticky='ew', padx=10, pady=5)
            
            # Configure card grid
            card.grid_columnconfigure(1, weight=1)
            
            # Room type header
            ttk.Label(
                card,
                text=room_type,
                style='RoomHeader.TLabel'
            ).grid(row=0, column=0, columnspan=2, sticky='w', padx=10, pady=5)
            
            # Price and Capacity
            ttk.Label(
                card,
                text=f"Price per night: ${price:.2f} | Capacity: {capacity} rooms",
                style='RoomPrice.TLabel'
            ).grid(row=1, column=0, columnspan=2, sticky='w', padx=10, pady=2)
            
            # Description
            ttk.Label(
                card,
                text=description,
                style='RoomDescription.TLabel',
                wraplength=700
            ).grid(row=2, column=0, columnspan=2, sticky='w', padx=10, pady=5)
    
    def _configure_styles(self):
        """Configure custom styles for room cards"""
        style = ttk.Style()
        
        # Card style
        style.configure('Card.TFrame', background='#ffffff')
        
        # Label styles
        style.configure('RoomHeader.TLabel',
                       font=('Arial', 16, 'bold'),
                       foreground='#2c3e50')
        
        style.configure('RoomPrice.TLabel',
                       font=('Arial', 14),
                       foreground='#27ae60')
        
        style.configure('RoomDescription.TLabel',
                       font=('Arial', 11),
                       foreground='#7f8c8d')

class RestaurantMenuWindow(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title("Restaurant Menu")
        self.geometry("300x400")
        
        # Create main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Menu items
        self.items = {
            "Tea": 20, "Coffee": 25, "Sandwich": 70,
            "Burger": 50, "Pizza": 150
        }
        
        self.selected_items = []
        
        for idx, (item, price) in enumerate(self.items.items(), start=1):
            ttk.Checkbutton(
                main_frame,
                text=f"{item} - Rs.{price}",
                command=lambda i=item: self.toggle_item(i)
            ).grid(row=idx, column=0, padx=5, pady=5, sticky='w')
        
        # Calculate bill button
        calculate_btn = ttk.Button(main_frame, text="Calculate Bill", command=self.calculate_bill)
        calculate_btn.grid(row=len(self.items)+1, column=0, padx=5, pady=10)
        
    def toggle_item(self, item):
        if item in self.selected_items:
            self.selected_items.remove(item)
        else:
            self.selected_items.append(item)
            
    def calculate_bill(self):
        total = sum(self.items[item] for item in self.selected_items)
        messagebox.showinfo("Bill", f"Total Bill: Rs.{total}")

if __name__ == "__main__":
    database_service = DatabaseService()
    room_service = RoomService(database_service)
    app = HotelManagementApp(database_service, room_service)
    app.mainloop()

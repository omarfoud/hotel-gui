"""
Base Window Module

Design Patterns:
1. Template Method Pattern:
   - BaseWindow defines skeleton of window creation
   - Subclasses implement _create_widgets method

2. Bridge Pattern:
   - Separates window abstraction from implementation
   - Allows both to vary independently

3. Composite Pattern:
   - Windows composed of widgets and frames
   - Uniform treatment of window components

SOLID Principles:
1. Single Responsibility Principle (SRP):
   - Each window class has a single purpose
   - BaseWindow handles only common window functionality

2. Open/Closed Principle (OCP):
   - New window types can be added without modifying base classes
   - Window behavior is extensible

3. Interface Segregation Principle (ISP):
   - Clean interfaces for window creation
   - Subclasses implement only needed methods

4. Dependency Inversion Principle (DIP):
   - Depends on abstractions (ABC)
   - Implementation details isolated in subclasses

5. Liskov Substitution Principle (LSP):
   - Window types are interchangeable
   - Maintains consistent behavior
"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod

class BaseWindow(tk.Toplevel, ABC):
    """
    # Design Pattern: Template Method
    # SOLID Principle: Open/Closed Principle (OCP)
    # Base class that defines window structure, extensible through subclassing
    """
    
    def __init__(self, root, title: str, geometry: str = "600x400"):
        """
        # Design Pattern: Bridge Pattern
        # SOLID Principle: Dependency Inversion Principle (DIP)
        # Depends on abstractions (tk.Toplevel) rather than concrete implementations
        """
        super().__init__(root)
        self._init_window(title, geometry)
        self._create_widgets()
    
    def _init_window(self, title: str, geometry: str):
        """
        # Design Pattern: Template Method
        # SOLID Principle: Single Responsibility Principle (SRP)
        # Handles only window initialization logic
        """
        self.title(title)
        self.geometry(geometry)
        self.configure(bg='#f0f0f0')
        
        # Create main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
    
    @abstractmethod
    def _create_widgets(self):
        """Abstract method to create window-specific widgets"""
        pass
    
    def show_header(self, text: str):
        """Display header with consistent styling"""
        header = ttk.Label(
            self.main_frame,
            text=text,
            style='Header.TLabel'
        )
        header.grid(row=0, column=0, columnspan=2, pady=20)
    
    def create_form_field(self, label: str, row: int, column: int = 0, width: int = 40):
        """Create a labeled form field"""
        ttk.Label(self.main_frame, text=label).grid(
            row=row, column=column, padx=5, pady=5, sticky='e'
        )
        entry = ttk.Entry(self.main_frame, width=width)
        entry.grid(row=row, column=column + 1, padx=5, pady=5, sticky='w')
        return entry
    
    def create_button(self, text: str, command, row: int, column: int, columnspan: int = 2):
        """Create a styled button"""
        button = ttk.Button(self.main_frame, text=text, command=command)
        button.grid(row=row, column=column, columnspan=columnspan, pady=10)
        return button
    
    def create_combobox(self, values: list, row: int, column: int, width: int = 37):
        """Create a combobox with values"""
        combo = ttk.Combobox(self.main_frame, values=values, width=width)
        combo.grid(row=row, column=column, padx=5, pady=5, sticky='w')
        return combo

class BaseFormWindow(BaseWindow):
    """
    # Design Pattern: Composite Pattern
    # SOLID Principle: Interface Segregation Principle (ISP)
    # Specific interface for form-based windows
    """
    
    def __init__(self, root, title: str, geometry: str = "600x400"):
        self.entries = {}
        super().__init__(root, title, geometry)
    
    def add_form_field(self, label: str, field_name: str, row: int):
        """Add a form field and store it in entries dictionary"""
        self.entries[field_name] = self.create_form_field(label, row)
    
    def get_form_data(self) -> dict:
        """Get all form data as a dictionary"""
        return {
            field: entry.get().strip() 
            for field, entry in self.entries.items()
        }
    
    def clear_form(self):
        """Clear all form fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

class BaseTableWindow(BaseWindow):
    """
    # Design Pattern: Composite Pattern
    # SOLID Principle: Interface Segregation Principle (ISP)
    # Specific interface for table-based windows
    """
    
    def __init__(self, root, title: str, columns: tuple, geometry: str = "800x600"):
        self.columns = columns
        super().__init__(root, title, geometry)
    
    def _create_widgets(self):
        """Create table with scrollbar"""
        # Create frame for buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # Create frame for table
        self.table_frame = ttk.Frame(self.main_frame)
        self.table_frame.grid(row=1, column=0, sticky='nsew')
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Create Treeview
        self.tree = ttk.Treeview(self.table_frame, columns=self.columns, show='headings')
        
        # Configure columns
        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by(c))
            self.tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid table and scrollbar
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Configure table frame grid
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)
    
    def sort_by(self, column: str):
        """Sort table by column"""
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]
        items.sort()
        for idx, (_, item) in enumerate(items):
            self.tree.move(item, '', idx)
    
    def clear_table(self):
        """Clear all items from table"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def add_row(self, values: tuple):
        """Add a row to the table"""
        self.tree.insert('', 'end', values=values)

class DataServiceMixin:
    """
    # Design Pattern: Mixin Pattern
    # SOLID Principle: Interface Segregation Principle (ISP)
    # Provides optional database functionality to windows
    """
    
    def __init__(self, database_service, *args, **kwargs):
        self.database_service = database_service
        super().__init__(*args, **kwargs)
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute database query"""
        return self.database_service.execute_query(query, params)
    
    def fetch_query(self, query: str, params: tuple = ()):
        """Fetch data from database"""
        return self.database_service.fetch_query(query, params)

"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# -------------------- Cafe App Schemas --------------------

class Cafe(BaseModel):
    """
    Cafe details
    Collection: "cafe"
    """
    name: str = Field(..., description="Cafe name")
    description: str = Field(..., description="Short description of the cafe")
    place: str = Field(..., description="Location/address of the cafe")
    phone: Optional[str] = Field(None, description="Contact phone number")
    open_hours: Optional[str] = Field(None, description="Opening hours information")

class MenuItem(BaseModel):
    """
    Menu items
    Collection: "menuitem"
    """
    name: str = Field(..., description="Name of the menu item")
    description: Optional[str] = Field(None, description="Item description")
    price: float = Field(..., ge=0, description="Price of the item")
    category: Optional[str] = Field(None, description="Category, e.g., Coffee, Pastry")
    image_url: Optional[str] = Field(None, description="Image URL for the item")

class OrderItem(BaseModel):
    menu_item_id: str = Field(..., description="Referenced MenuItem ID")
    quantity: int = Field(..., ge=1, description="Quantity of the item")

class Order(BaseModel):
    """
    Orders placed by customers
    Collection: "order"
    """
    customer_name: str = Field(..., description="Customer full name")
    contact: Optional[str] = Field(None, description="Phone or email")
    items: List[OrderItem] = Field(default_factory=list, description="List of items in the order")
    note: Optional[str] = Field(None, description="Special instructions")
    total: Optional[float] = Field(None, ge=0, description="Computed total amount")
    status: str = Field("pending", description="Order status")

class Reservation(BaseModel):
    """
    Table reservations
    Collection: "reservation"
    """
    name: str = Field(..., description="Guest name")
    contact: Optional[str] = Field(None, description="Phone or email")
    party_size: int = Field(..., ge=1, description="Number of guests")
    datetime_iso: str = Field(..., description="Reservation date/time in ISO format")
    notes: Optional[str] = Field(None, description="Additional notes")

# -------------------- Example Schemas (kept for reference) --------------------

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

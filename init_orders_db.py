#!/usr/bin/env python
"""Initialize order tables in the database."""

from app import app, db
from models import Order, OrderItem

with app.app_context():
    # Create Order and OrderItem tables
    db.create_all()
    
    print("✅ Order tables initialized successfully!")
    print("   - orders table created")
    print("   - order_items table created")
    print("\nOrderManagement System Ready!")

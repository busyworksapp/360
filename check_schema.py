#!/usr/bin/env python
"""Check database schema and apply migrations"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("Tables in database:", tables)
    print("\nTransaction table schema:")
    if 'transactions' in tables:
        columns = inspector.get_columns('transactions')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    
    print("\nOrders table schema:")
    if 'orders' in tables:
        columns = inspector.get_columns('orders')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

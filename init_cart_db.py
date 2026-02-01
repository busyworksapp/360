#!/usr/bin/env python
"""
Database initialization script for Cart functionality
"""
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db  # noqa: E402


def init_cart_tables():
    """Create cart and cart_item tables"""
    with app.app_context():
        try:
            # Create the tables
            db.create_all()
            print("✓ Database tables created/updated successfully!")
            print("✓ Cart and CartItem tables are ready")
            return 0
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            return 1


if __name__ == '__main__':
    exit_code = init_cart_tables()
    sys.exit(exit_code)

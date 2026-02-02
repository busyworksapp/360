#!/usr/bin/env python
"""
Setup script to create Invoice tables directly in the database
Run this script to initialize the invoice management system
"""

from app import app, db
from models import Invoice, InvoicePayment

if __name__ == '__main__':
    with app.app_context():
        # Create Invoice and InvoicePayment tables
        db.create_all()
        print("✓ Invoice and InvoicePayment tables created successfully!")
        print("\nInvoice Management System is now ready to use:")
        print("  - Admin Invoices: /admin/invoices")
        print("  - Customer Invoices: /customer/invoices")

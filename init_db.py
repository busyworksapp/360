#!/usr/bin/env python
"""Initialize the database with all required tables."""

from app import app, db
from models import (
    User, SiteSettings, CompanyInfo, Service, Product,
    HeroSection, ContentSection, PaymentMethod, PaymentTerm,
    Transaction, ContactSubmission, MenuItem, Testimonial
)

def init_database():
    """Create all database tables."""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if admin user exists
        admin_exists = User.query.filter_by(email='admin@360degreesupply.co.za').first()
        
        if not admin_exists:
            print("Creating default admin user...")
            admin = User(email='admin@360degreesupply.co.za', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created!")
            print("  Email: admin@360degreesupply.co.za")
            print("  Password: admin123")
        else:
            print("✓ Admin user already exists")
        
        # Create default company info if it doesn't exist
        company = CompanyInfo.query.first()
        if not company:
            print("Creating default company info...")
            company = CompanyInfo(
                company_name='360Degree Supply (Pty) Ltd',
                address='South Africa',
                phone='+27 (0)xx xxx xxxx',
                email='info@360degreesupply.co.za',
                description='Your trusted supply partner',
                mission='To provide quality supply solutions'
            )
            db.session.add(company)
            db.session.commit()
            print("✓ Default company info created!")
        else:
            print("✓ Company info already exists")
        
        print("\n✅ Database initialization complete!")

if __name__ == '__main__':
    init_database()

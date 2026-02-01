#!/usr/bin/env python
"""
Production Database Initialization Script
=========================================
This script initializes the production database with:
- All required tables and schemas
- Payment methods (Stripe, PayFast)
- Payment terms
- Company information
- Admin user (optional)

Usage:
    python init_production.py

Environment Variables Required:
    - DATABASE_URL: Connection string (postgresql://... or sqlite://...)
    - FLASK_ENV: Set to 'production'

Author: 360Degree Supply Development Team
Version: 1.0.0
Date: January 31, 2026
"""

import os
import sys
import logging

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (
    PaymentMethod,
    PaymentTerm,
    CompanyInfo,
    User
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print banner"""
    print("\n" + "=" * 70)
    print("  360Degree Supply - Production Database Initialization")
    print("  Version 1.0.0 | January 31, 2026")
    print("=" * 70 + "\n")


def verify_environment():
    """Verify environment configuration"""
    logger.info("Verifying environment configuration...")
    
    required_vars = ['FLASK_ENV', 'DATABASE_URL']
    missing = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        logger.error("Please set environment variables and try again.")
        return False
    
    # Verify DATABASE_URL format
    db_url = os.environ.get('DATABASE_URL', '')
    if not (db_url.startswith('postgresql://') or
            db_url.startswith('sqlite://')):
        logger.error("DATABASE_URL must start with 'postgresql://' or "
                     "'sqlite://'")
        return False
    
    logger.info("✓ Environment configuration verified")
    return True


def create_database_tables():
    """Create database tables"""
    logger.info("Creating database tables...")
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            logger.info("✓ Database tables created successfully")
            return True
    except Exception as e:
        logger.error(f"✗ Error creating tables: {str(e)}")
        return False


def load_payment_methods():
    """Load payment methods"""
    logger.info("Loading payment methods...")
    
    try:
        with app.app_context():
            # Check if already loaded
            existing = PaymentMethod.query.count()
            if existing > 0:
                logger.info(
                    f"✓ Payment methods already exist ({existing} methods)"
                )
                return True
            
            # Create payment methods
            methods = [
                PaymentMethod(
                    name='Stripe',
                    description='Credit/Debit Card via Stripe',
                    gateway='stripe',
                    is_active=True,
                    order_position=1
                ),
                PaymentMethod(
                    name='PayFast',
                    description='South African Payment Gateway',
                    gateway='payfast',
                    is_active=True,
                    order_position=2
                )
            ]
            
            for method in methods:
                db.session.add(method)
            
            db.session.commit()
            logger.info(f"✓ Loaded {len(methods)} payment methods")
            return True
            
    except Exception as e:
        logger.error(f"✗ Error loading payment methods: {str(e)}")
        db.session.rollback()
        return False


def load_payment_terms():
    """Load payment terms"""
    logger.info("Loading payment terms...")
    
    try:
        with app.app_context():
            # Check if already loaded
            existing = PaymentTerm.query.count()
            if existing > 0:
                logger.info(
                    f"✓ Payment terms already exist ({existing} terms)"
                )
                return True
            
            # Create payment terms
            terms = [
                PaymentTerm(
                    name='Full Payment',
                    description='Pay full amount upfront',
                    days=0,
                    is_active=True,
                    order_position=1
                ),
                PaymentTerm(
                    name='Net 30',
                    description='Payment due within 30 days',
                    days=30,
                    is_active=True,
                    order_position=2
                ),
                PaymentTerm(
                    name='Net 60',
                    description='Payment due within 60 days',
                    days=60,
                    is_active=True,
                    order_position=3
                )
            ]
            
            for term in terms:
                db.session.add(term)
            
            db.session.commit()
            logger.info(f"✓ Loaded {len(terms)} payment terms")
            return True
            
    except Exception as e:
        logger.error(f"✗ Error loading payment terms: {str(e)}")
        db.session.rollback()
        return False


def load_company_info():
    """Load company information"""
    logger.info("Loading company information...")
    
    try:
        with app.app_context():
            # Check if already loaded
            existing = CompanyInfo.query.first()
            if existing:
                logger.info(f"✓ Company info already exists: {existing.company_name}")
                return True
            
            # Create company info
            company = CompanyInfo(
                company_name='360Degree Supply',
                email='info@360degreesupply.co.za',
                phone='+27 64 902 4363',
                address='123 Business Street',
                city='Johannesburg',
                state='Gauteng',
                country='South Africa',
                postal_code='2000',
                registration_number='2020/123456/07',
                tax_number='9876543210'
            )
            
            db.session.add(company)
            db.session.commit()
            logger.info("✓ Company information loaded")
            return True
            
    except Exception as e:
        logger.error(f"✗ Error loading company info: {str(e)}")
        db.session.rollback()
        return False


def create_admin_user():
    """Create admin user (optional)"""
    logger.info("Checking for admin user...")
    
    try:
        with app.app_context():
            # Check if admin exists
            existing = User.query.filter_by(is_admin=True).first()
            if existing:
                logger.info(f"✓ Admin user already exists: {existing.email}")
                return True
            
            # Ask user for admin credentials
            print("\n" + "=" * 70)
            print("  ADMIN USER SETUP")
            print("=" * 70)
            
            email = input("Enter admin email: ").strip()
            if not email:
                logger.info("Skipping admin user creation")
                return True
            
            password = input("Enter admin password (min 8 characters): ").strip()
            if len(password) < 8:
                logger.warning("Password must be at least 8 characters")
                return False
            
            # Create admin
            admin = User(
                email=email,
                is_admin=True
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            logger.info(f"✓ Admin user created: {email}")
            return True
            
    except Exception as e:
        logger.error(f"✗ Error creating admin: {str(e)}")
        db.session.rollback()
        return False


def verify_database():
    """Verify database setup"""
    logger.info("Verifying database setup...")
    
    try:
        with app.app_context():
            # Count records in each table
            payment_methods = PaymentMethod.query.count()
            payment_terms = PaymentTerm.query.count()
            company_info = CompanyInfo.query.count()
            
            logger.info(f"✓ Payment Methods: {payment_methods}")
            logger.info(f"✓ Payment Terms: {payment_terms}")
            logger.info(f"✓ Company Info: {company_info}")
            
            if payment_methods > 0 and payment_terms > 0 and company_info > 0:
                logger.info("✓ Database verification successful")
                return True
            else:
                logger.warning("⚠ Some data is missing")
                return False
                
    except Exception as e:
        logger.error(f"✗ Error verifying database: {str(e)}")
        return False


def print_summary():
    """Print summary"""
    print("\n" + "=" * 70)
    print("  DATABASE INITIALIZATION COMPLETE")
    print("=" * 70)
    print("\nNext Steps:")
    print("  1. Verify configuration in .env")
    print("  2. Run tests: pytest test_payments.py -v")
    print("  3. Start application: gunicorn -w 4 -b 0.0.0.0:8000 app:app")
    print("  4. Test payment routes in browser")
    print("  5. Verify webhooks in payment gateway dashboards")
    print("\nFor more information:")
    print("  - See: DEPLOYMENT_GUIDE.md")
    print("  - Issues: TROUBLESHOOTING_GUIDE.md")
    print("=" * 70 + "\n")


def main():
    """Main initialization sequence"""
    print_banner()
    
    # Verify environment
    if not verify_environment():
        sys.exit(1)
    
    # Create database tables
    if not create_database_tables():
        sys.exit(1)
    
    # Load initial data
    if not load_payment_methods():
        sys.exit(1)
    
    if not load_payment_terms():
        sys.exit(1)
    
    if not load_company_info():
        sys.exit(1)
    
    # Optional: Create admin user
    create_admin_user()
    
    # Verify database
    if not verify_database():
        logger.warning("⚠ Database verification found issues")
    
    # Print summary
    print_summary()
    logger.info("✓ Production database initialization complete!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Initialization cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

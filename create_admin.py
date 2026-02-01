#!/usr/bin/env python
"""
Script to create an admin user for the application
"""

from app import app, db
from models import User

def create_admin_user(email, password):
    """Create a new admin user"""
    with app.app_context():
        # Check if user already exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"❌ User with email '{email}' already exists!")
            return False
        
        # Create new admin user
        admin = User(
            email=email,
            is_admin=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"\nYou can now login at: http://127.0.0.1:5000/admin/login")
        return True

if __name__ == '__main__':
    # Create admin user with default credentials
    email = 'admin@360degree.com'
    password = 'admin123'
    
    print("Creating admin user...")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print()
    
    create_admin_user(email, password)

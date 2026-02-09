"""
Master Admin Setup Verification Script
Run this to ensure all master admin tables and functions are ready
"""

from app import app, db
from models import User
from models.master_admin import MasterAdmin, SecurityEvent, UserActivity, SystemLog
from werkzeug.security import generate_password_hash
from datetime import datetime

def setup_master_admin():
    with app.app_context():
        print("🔧 Setting up Master Admin...")
        
        # Create all tables
        print("📊 Creating database tables...")
        db.create_all()
        print("✅ Tables created")
        
        # Check for master admin user
        master_email = "donfabio@360degreesupply.co.za"
        user = User.query.filter_by(email=master_email).first()
        
        if not user:
            print(f"👤 Creating master admin user: {master_email}")
            user = User(
                email=master_email,
                is_admin=True
            )
            user.password_hash = generate_password_hash("Dot@com12345")
            db.session.add(user)
            db.session.commit()
            print("✅ Master admin user created")
        else:
            print(f"✅ Master admin user exists: {master_email}")
        
        # Check for master admin profile
        master_profile = MasterAdmin.query.filter_by(user_id=user.id).first()
        
        if not master_profile:
            print("🔐 Creating master admin profile...")
            master_profile = MasterAdmin(
                user_id=user.id,
                is_active=True,
                granted_by=user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(master_profile)
            db.session.commit()
            print("✅ Master admin profile created")
        else:
            print("✅ Master admin profile exists")
        
        # Verify tables
        print("\n📋 Verifying tables...")
        tables = ['users', 'master_admins', 'security_events', 'user_activities', 
                  'system_logs', 'audit_logs', 'customers', 'products', 'orders', 
                  'invoices', 'transactions']
        
        for table in tables:
            try:
                result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  ✅ {table}: {count} records")
            except Exception as e:
                print(f"  ❌ {table}: Error - {str(e)}")
        
        print("\n🎉 Master Admin setup complete!")
        print(f"\n📧 Login Email: {master_email}")
        print("🔑 Password: Dot@com12345")
        print("🌐 Access: /master-admin/dashboard")
        print("\n⚠️  IMPORTANT: Change the password after first login!")

if __name__ == "__main__":
    setup_master_admin()

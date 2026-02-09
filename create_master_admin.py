from app import app, db
from models import User
from models.master_admin import MasterAdmin
import sys

def create_master_admin(email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"✗ User {email} not found")
            return
        
        if hasattr(user, 'master_admin_profile') and user.master_admin_profile:
            print(f"✓ {email} is already a Master Admin")
            return
        
        master_admin = MasterAdmin(user_id=user.id, is_active=True)
        db.session.add(master_admin)
        db.session.commit()
        
        print(f"✓ {email} promoted to Master Admin")
        print(f"  User ID: {user.id}")
        print(f"  Access: /master-admin/dashboard")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python create_master_admin.py <email>")
        sys.exit(1)
    
    create_master_admin(sys.argv[1])

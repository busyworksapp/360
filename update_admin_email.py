"""Update Admin Email to Real Address"""
from app import app, db
from models import User

def update_admin_email():
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(role='admin').first()
        
        if not admin:
            print("[ERROR] No admin user found!")
            return
        
        # Update email
        new_email = 'support@360degreesupply.co.za'
        old_email = admin.email
        
        admin.email = new_email
        admin.email_verified = True
        
        db.session.commit()
        
        print("=" * 60)
        print("ADMIN EMAIL UPDATED")
        print("=" * 60)
        print(f"[OK] Old email: {old_email}")
        print(f"[OK] New email: {new_email}")
        print(f"[OK] Email verified: Yes")
        print("\n[INFO] Admin can now login with:")
        print(f"       Email: {new_email}")
        print("       Password: (current admin password)")
        print("=" * 60)

if __name__ == '__main__':
    update_admin_email()

"""Setup Master Admin user - Create user and promote to Master Admin"""
from app import app, db
from models import User
from models.master_admin import MasterAdmin

def setup_master_admin():
    with app.app_context():
        email = 'donfabio@360degreesupply.co.za'
        password = 'Dot@com12345'
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new admin user
            user = User(email=email, is_admin=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f'✅ Created admin user: {email}')
        else:
            print(f'✅ User already exists: {email}')
        
        # Check if already Master Admin
        master_admin = MasterAdmin.query.filter_by(user_id=user.id).first()
        
        if not master_admin:
            # Promote to Master Admin
            master_admin = MasterAdmin(
                user_id=user.id,
                granted_by=user.id,
                is_active=True
            )
            db.session.add(master_admin)
            db.session.commit()
            print(f'✅ Promoted {email} to Master Admin')
        else:
            print(f'✅ {email} is already a Master Admin')
        
        print(f'\n🎉 Setup complete!')
        print(f'Email: {email}')
        print(f'Password: {password}')
        print(f'Access: /master-admin/dashboard')

if __name__ == '__main__':
    setup_master_admin()

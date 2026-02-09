"""Setup Master Admin user"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask
from config import Config
from models import db, User
import sys
sys.path.insert(0, 'models')
from master_admin import MasterAdmin

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    email = 'donfabio@360degreesupply.co.za'
    password = 'Dot@com12345'
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    
    if not user:
        user = User(email=email, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f'Created admin user: {email}')
    else:
        print(f'User already exists: {email}')
    
    # Check if already Master Admin
    master_admin = MasterAdmin.query.filter_by(user_id=user.id).first()
    
    if not master_admin:
        master_admin = MasterAdmin(
            user_id=user.id,
            granted_by=user.id,
            is_active=True
        )
        db.session.add(master_admin)
        db.session.commit()
        print(f'Promoted {email} to Master Admin')
    else:
        print(f'{email} is already a Master Admin')
    
    print(f'\nSetup complete!')
    print(f'Email: {email}')
    print(f'Password: {password}')
    print(f'Access: /master-admin/dashboard')

"""Update Admin Email - No Unicode Version"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Disable logging temporarily
os.environ['FLASK_SKIP_LOGGING'] = '1'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

with app.app_context():
    try:
        # Update admin email
        admin = User.query.filter_by(id=1).first()
        if admin:
            admin.email = 'support@360degreesupply.co.za'
            print(f"[OK] Updated admin email to: {admin.email}")
        
        # Delete duplicate admin
        duplicate = User.query.filter_by(id=2).first()
        if duplicate:
            db.session.delete(duplicate)
            print("[OK] Deleted duplicate admin account")
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("ADMIN EMAIL UPDATE COMPLETE")
        print("="*60)
        print("Email: support@360degreesupply.co.za")
        print("Password: (your current admin password)")
        print("="*60)
        
    except Exception as e:
        print(f"[ERROR] {e}")

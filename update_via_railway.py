"""
Update Admin Email via Railway CLI
Run: railway run python update_via_railway.py
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['FLASK_SKIP_LOGGING'] = '1'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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
        admin = User.query.filter_by(id=1).first()
        if admin:
            admin.email = 'support@360degreesupply.co.za'
            print(f"Updated: {admin.email}")
        
        duplicate = User.query.filter_by(id=2).first()
        if duplicate:
            db.session.delete(duplicate)
            print("Deleted duplicate")
        
        db.session.commit()
        print("\nSUCCESS: Admin email = support@360degreesupply.co.za")
        
    except Exception as e:
        print(f"ERROR: {e}")

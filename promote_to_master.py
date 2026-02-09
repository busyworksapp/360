from app import app, db
from models import User
from models.master_admin import MasterAdmin

with app.app_context():
    user = User.query.filter_by(email='donfabio@360degreesupply.co.za').first()
    if user:
        existing = MasterAdmin.query.filter_by(user_id=user.id).first()
        if not existing:
            master = MasterAdmin(user_id=user.id, is_active=True)
            db.session.add(master)
            db.session.commit()
            print(f"✓ {user.email} promoted to Master Admin")
        else:
            print(f"✓ {user.email} is already Master Admin")
    else:
        print("✗ User not found")

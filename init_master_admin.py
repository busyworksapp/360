from app import app, db
from models.master_admin import MasterAdmin, AuditLog, SecurityEvent, SystemLog, UserActivity

with app.app_context():
    print("Creating Master Admin tables...")
    db.create_all()
    print("✓ Tables created successfully!")
    print("\nCreated tables:")
    print("- master_admins")
    print("- audit_logs")
    print("- security_events")
    print("- system_logs")
    print("- user_activities")

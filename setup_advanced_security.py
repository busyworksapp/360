"""
Setup Advanced Security Features
Run this to create all necessary tables for IP blocking, system control, and monitoring
"""

from app import app, db
from models.security_models import BlockedIP, SystemControl, UserPermission, DetailedLog
from models.master_admin import MasterAdmin, SecurityEvent, UserActivity, SystemLog
from models import User
from datetime import datetime

def setup_advanced_security():
    with app.app_context():
        print("🔒 Setting up Advanced Security Features...")
        
        # Create all tables
        print("📊 Creating database tables...")
        db.create_all()
        print("✅ Tables created")
        
        # Initialize system control
        print("🎛️ Initializing system control...")
        control = SystemControl.query.first()
        if not control:
            control = SystemControl(
                is_system_active=True,
                maintenance_mode=False
            )
            db.session.add(control)
            db.session.commit()
            print("✅ System control initialized")
        else:
            print("✅ System control already exists")
        
        # Verify tables
        print("\n📋 Verifying tables...")
        tables = [
            'blocked_ips',
            'system_controls',
            'user_permissions',
            'detailed_logs',
            'master_admins',
            'security_events',
            'user_activities',
            'system_logs'
        ]
        
        for table in tables:
            try:
                result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  ✅ {table}: {count} records")
            except Exception as e:
                print(f"  ❌ {table}: Error - {str(e)}")
        
        print("\n🎉 Advanced Security Setup Complete!")
        print("\n📚 Features Available:")
        print("  • IP Blocking (permanent & temporary)")
        print("  • System Control (shutdown & maintenance)")
        print("  • User Permissions (access & sidebar control)")
        print("  • Detailed Logs (color-coded severity)")
        print("  • Live Monitoring (real-time updates)")
        print("  • Deep Dive Investigation")
        print("  • Analytics & Insights")
        
        print("\n🌐 Access URLs:")
        print("  • Blocked IPs: /master-admin/security/blocked-ips")
        print("  • System Control: /master-admin/system/control")
        print("  • Live Logs: /master-admin/logs/live")
        print("  • Detailed Logs: /master-admin/logs/detailed")
        print("  • Analytics: /master-admin/analytics")
        
        print("\n⚠️  IMPORTANT:")
        print("  • Only master admins can access these features")
        print("  • System shutdown blocks all users except master admins")
        print("  • IP blocking is immediate and effective")
        print("  • All actions are logged and audited")

if __name__ == "__main__":
    setup_advanced_security()

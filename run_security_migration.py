"""
Create Security Tables Migration
Run this to create all missing security tables in the database
"""

from app import app, db
from sqlalchemy import text

def create_security_tables():
    with app.app_context():
        print("🔧 Creating security tables...")
        
        try:
            # Read SQL file
            with open('migrations/create_security_tables.sql', 'r') as f:
                sql_script = f.read()
            
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in statements:
                if statement:
                    try:
                        db.session.execute(text(statement))
                        db.session.commit()
                    except Exception as e:
                        print(f"⚠️  Statement warning: {str(e)}")
                        db.session.rollback()
            
            print("✅ Security tables created successfully!")
            
            # Verify tables
            print("\n📊 Verifying tables...")
            tables = ['blocked_ips', 'system_controls', 'user_permissions', 'detailed_logs']
            
            for table in tables:
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  ✅ {table}: {count} records")
                except Exception as e:
                    print(f"  ❌ {table}: {str(e)}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    create_security_tables()

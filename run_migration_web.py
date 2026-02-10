"""
Web-based Migration Runner
Visit /run-migration in your browser to execute the migration
"""

from flask import Flask, jsonify
from app import app, db
from sqlalchemy import text

@app.route('/run-migration')
def run_migration():
    """Execute security tables migration"""
    results = []
    
    try:
        # Read SQL file
        with open('migrations/create_security_tables.sql', 'r') as f:
            sql_script = f.read()
        
        # Split and execute statements
        statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for statement in statements:
            if statement and not statement.startswith('SELECT'):
                try:
                    db.session.execute(text(statement))
                    db.session.commit()
                    results.append(f"✅ Executed: {statement[:50]}...")
                except Exception as e:
                    results.append(f"⚠️ Warning: {str(e)[:100]}")
                    db.session.rollback()
        
        # Verify tables
        tables = ['blocked_ips', 'system_controls', 'user_permissions', 'detailed_logs']
        verification = []
        
        for table in tables:
            try:
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                verification.append(f"✅ {table}: {count} records")
            except Exception as e:
                verification.append(f"❌ {table}: Failed")
        
        return jsonify({
            'status': 'success',
            'message': 'Migration completed',
            'results': results,
            'verification': verification
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == "__main__":
    print("Add this route to your app.py or visit /run-migration in your browser")

"""
SIMPLE PRODUCTION DATABASE RESET
Direct SQL approach - no app import needed
"""
import os
from dotenv import load_dotenv
import pymysql

load_dotenv()

def reset_database():
    """Reset database using direct SQL"""
    
    print("=" * 60)
    print("PRODUCTION DATABASE RESET")
    print("=" * 60)
    print("\nWARNING: This will delete ALL demo data!")
    
    confirm = input("\nType 'RESET' to confirm: ")
    if confirm != 'RESET':
        print("Aborted.")
        return
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL not found in .env")
        return
    
    # Parse MySQL URL
    # Format: mysql://user:pass@host:port/dbname
    try:
        parts = db_url.replace('mysql://', '').split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')
        host_port = host_db[0].split(':')
        
        connection = pymysql.connect(
            host=host_port[0],
            port=int(host_port[1]) if len(host_port) > 1 else 3306,
            user=user_pass[0],
            password=user_pass[1],
            database=host_db[1],
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        print("\n[DELETE] Removing demo data...")
        
        # Delete in correct order (respecting foreign keys)
        tables = [
            'proof_of_payments',
            'invoice_payments',
            'invoice_items',
            'invoices',
            'transactions',
            'order_items',
            'orders',
            'cart_items',
            'carts',
            'customers',
            'products',
            'services',
            'testimonials',
            'hero_sections',
            'contact_submissions'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                count = cursor.rowcount
                print(f"  [OK] Deleted {count} rows from {table}")
            except Exception as e:
                print(f"  [SKIP] {table}: {str(e)}")
        
        # Keep audit logs for security
        # cursor.execute("DELETE FROM audit_logs")
        
        connection.commit()
        
        print("\n[OK] Demo data deleted!")
        
        # Check admin account
        cursor.execute("SELECT COUNT(*) FROM users WHERE email='admin@360degreesupply.co.za'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("\n[WARN] No admin account found!")
            print("Create admin account manually or run init_db.py")
        else:
            print("\n[OK] Admin account exists")
        
        # Summary
        print("\n" + "=" * 60)
        print("DATABASE SUMMARY")
        print("=" * 60)
        
        for table in ['users', 'customers', 'products', 'services', 'orders', 'invoices']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count}")
            except:
                pass
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("[OK] DATABASE READY FOR PRODUCTION!")
        print("=" * 60)
        
        print("\n[NEXT STEPS]")
        print("  1. Add real products via /admin/products/add")
        print("  2. Add real services via /admin/services/add")
        print("  3. Update company info via /admin/company")
        print("  4. Enable 2FA for admin via /admin/2fa/setup")
        print("  5. Deploy to production")
        
    except Exception as e:
        print(f"\n[ERROR] Database operation failed: {str(e)}")
        print("Make sure DATABASE_URL is correct in .env file")

if __name__ == '__main__':
    reset_database()

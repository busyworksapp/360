"""Update Admin Email - Simple SQL Version"""
import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'barron_db',
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Update admin email
    cursor.execute("""
        UPDATE users 
        SET email = 'support@360degreesupply.co.za',
            email_verified = 1
        WHERE role = 'admin'
    """)
    
    conn.commit()
    
    print("=" * 60)
    print("ADMIN EMAIL UPDATED")
    print("=" * 60)
    print("[OK] Admin email: support@360degreesupply.co.za")
    print("[OK] Email verified: Yes")
    print("\nAdmin can now login with:")
    print("  Email: support@360degreesupply.co.za")
    print("  Password: (current admin password)")
    print("=" * 60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"[ERROR] {e}")
    print("\nMake sure MySQL is running!")

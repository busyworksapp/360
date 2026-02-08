"""Update Admin Email - Railway Database"""
import pymysql

print("=" * 60)
print("UPDATE ADMIN EMAIL TO REAL ADDRESS")
print("=" * 60)
print("\nGet your Railway MySQL connection details:")
print("1. Go to Railway Dashboard")
print("2. Click MySQL service")
print("3. Click 'Connect' tab")
print("4. Copy the TCP Proxy details\n")

host = input("Enter MySQL Host (e.g., monorail.proxy.rlwy.net): ").strip()
port = input("Enter MySQL Port (e.g., 12345): ").strip()
user = input("Enter MySQL User (default: root): ").strip() or "root"
password = input("Enter MySQL Password: ").strip()
database = input("Enter Database Name (default: railway): ").strip() or "railway"

print("\nConnecting to Railway MySQL...")

try:
    conn = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    print("[OK] Connected to database")
    
    # Update admin email
    cursor.execute("""
        UPDATE users 
        SET email = 'support@360degreesupply.co.za'
        WHERE id = 1
    """)
    print("[OK] Updated admin email")
    
    # Delete duplicate admin
    cursor.execute("DELETE FROM users WHERE id = 2")
    print("[OK] Deleted duplicate admin")
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT id, email, is_admin FROM users WHERE is_admin = 1")
    result = cursor.fetchone()
    
    print("\n" + "=" * 60)
    print("SUCCESS - ADMIN EMAIL UPDATED")
    print("=" * 60)
    print(f"ID: {result[0]}")
    print(f"Email: {result[1]}")
    print(f"Admin: {result[2]}")
    print("=" * 60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nMake sure:")
    print("- Railway MySQL service is running")
    print("- Connection details are correct")
    print("- Your IP is allowed (Railway allows all by default)")

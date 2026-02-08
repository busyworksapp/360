"""Update Admin Email - Uses .env file"""
import os
import re
from dotenv import load_dotenv
import pymysql

load_dotenv()

# Parse DATABASE_URL from .env
db_url = os.getenv('DATABASE_URL')
print(f"Database URL: {db_url}")

# Parse connection string
# Format: mysql+pymysql://user:password@host:port/database
match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)

if not match:
    print("[ERROR] Invalid DATABASE_URL format in .env")
    print("Expected: mysql+pymysql://user:password@host:port/database")
    exit(1)

user, password, host, port, database = match.groups()

print(f"Connecting to {host}:{port}/{database}...")

try:
    conn = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
        charset='utf8mb4',
        connect_timeout=10
    )
    cursor = conn.cursor()
    
    print("[OK] Connected")
    
    # Update admin email
    cursor.execute("UPDATE users SET email = 'support@360degreesupply.co.za' WHERE id = 1")
    print("[OK] Updated admin email")
    
    # Delete duplicate
    cursor.execute("DELETE FROM users WHERE id = 2")
    print("[OK] Deleted duplicate")
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT id, email FROM users WHERE is_admin = 1")
    result = cursor.fetchone()
    
    print("\n" + "="*60)
    print("SUCCESS")
    print("="*60)
    print(f"Admin Email: {result[1]}")
    print("="*60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"[ERROR] {e}")

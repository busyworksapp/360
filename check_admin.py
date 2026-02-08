"""
Check admin accounts in database
"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection
db_url = os.getenv('DATABASE_URL')
if db_url.startswith('mysql+pymysql://'):
    db_url = db_url.replace('mysql+pymysql://', '')

# Parse connection string
# Format: user:password@host:port/database
parts = db_url.split('@')
user_pass = parts[0].split(':')
host_db = parts[1].split('/')
host_port = host_db[0].split(':')

user = user_pass[0]
password = user_pass[1]
host = host_port[0]
port = int(host_port[1])
database = host_db[1]

print(f"Connecting to database: {host}:{port}/{database}")

try:
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    
    cursor = connection.cursor()
    
    # Query admin users
    cursor.execute("SELECT id, email, is_admin, two_factor_enabled FROM user WHERE is_admin = 1")
    
    admins = cursor.fetchall()
    
    if admins:
        print("\n=== ADMIN ACCOUNTS ===")
        for admin in admins:
            print(f"\nID: {admin[0]}")
            print(f"Email: {admin[1]}")
            print(f"Is Admin: {admin[2]}")
            print(f"2FA Enabled: {admin[3]}")
    else:
        print("\nNo admin accounts found!")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")

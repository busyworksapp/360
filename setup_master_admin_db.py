import os
import pymysql
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
db_url = os.getenv('DATABASE_URL', '')

if not db_url:
    print("ERROR: DATABASE_URL not found in environment")
    exit(1)

# Parse database URL
parsed = urlparse(db_url)

# Connect to database
conn = pymysql.connect(
    host=parsed.hostname,
    port=parsed.port or 3306,
    user=parsed.username,
    password=parsed.password,
    database=parsed.path.lstrip('/')
)

try:
    cursor = conn.cursor()
    
    # Create master_admins table
    print("Creating master_admins table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            is_active BOOLEAN DEFAULT TRUE,
            mfa_enabled BOOLEAN DEFAULT FALSE,
            mfa_secret VARCHAR(32),
            last_login DATETIME,
            last_ip VARCHAR(45),
            granted_by INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    print("Table created successfully")
    
    # Promote user to Master Admin
    print("Promoting donfabio@360degreesupply.co.za to Master Admin...")
    cursor.execute("""
        INSERT INTO master_admins (user_id, is_active, granted_by, created_at)
        SELECT id, TRUE, id, NOW()
        FROM users
        WHERE email = 'donfabio@360degreesupply.co.za'
        AND NOT EXISTS (
            SELECT 1 FROM master_admins WHERE user_id = users.id
        )
    """)
    conn.commit()
    
    if cursor.rowcount > 0:
        print("User promoted to Master Admin successfully")
    else:
        print("User is already a Master Admin or doesn't exist")
    
    # Verify
    cursor.execute("""
        SELECT u.id, u.email, u.is_admin, ma.is_active
        FROM users u
        LEFT JOIN master_admins ma ON u.id = ma.user_id
        WHERE u.email = 'donfabio@360degreesupply.co.za'
    """)
    result = cursor.fetchone()
    
    if result:
        print(f"\nVerification:")
        print(f"User ID: {result[0]}")
        print(f"Email: {result[1]}")
        print(f"Is Admin: {result[2]}")
        print(f"Master Admin Active: {result[3]}")
        print(f"\nSetup complete! Access at: /master-admin/dashboard")
    else:
        print("\nWARNING: User not found in database")
        print("Please create the user account first by logging in")
    
finally:
    cursor.close()
    conn.close()

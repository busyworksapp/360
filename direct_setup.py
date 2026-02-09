import os
import pymysql
from werkzeug.security import generate_password_hash
from urllib.parse import urlparse

# Database connection from environment
db_url = os.getenv('DATABASE_URL', '')
print(f"DB URL: {db_url[:50]}...")

# Parse URL
parsed = urlparse(db_url)
host = parsed.hostname
port = parsed.port or 3306
user = parsed.username
password = parsed.password
database = parsed.path.lstrip('/')

print(f"Connecting to: {host}:{port}/{database}")

# Connect to database
conn = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

try:
    cursor = conn.cursor()
    
    email = 'donfabio@360degreesupply.co.za'
    pwd = 'Dot@com12345'
    pwd_hash = generate_password_hash(pwd)
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user_row = cursor.fetchone()
    
    if not user_row:
        # Create user
        cursor.execute(
            "INSERT INTO users (email, password_hash, is_admin, created_at) VALUES (%s, %s, TRUE, NOW())",
            (email, pwd_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        print(f"Created user: {email} (ID: {user_id})")
    else:
        user_id = user_row[0]
        print(f"User exists: {email} (ID: {user_id})")
    
    # Create master_admins table if not exists
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
    print("Master admins table ready")
    
    # Check if already Master Admin
    cursor.execute("SELECT id FROM master_admins WHERE user_id = %s", (user_id,))
    ma_row = cursor.fetchone()
    
    if not ma_row:
        # Promote to Master Admin
        cursor.execute(
            "INSERT INTO master_admins (user_id, is_active, granted_by, created_at) VALUES (%s, TRUE, %s, NOW())",
            (user_id, user_id)
        )
        conn.commit()
        print(f"Promoted {email} to Master Admin")
    else:
        print(f"{email} is already a Master Admin")
    
    print("\nSetup complete!")
    print(f"Email: {email}")
    print(f"Password: {pwd}")
    print(f"Access: /master-admin/dashboard")
    
finally:
    cursor.close()
    conn.close()

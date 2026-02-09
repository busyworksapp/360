import os
import pymysql
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash

db_url = 'mysql://root:VJPYmDrwdrfKuCcGVJffXMyeTLzrkAUo@ballast.proxy.rlwy.net:14911/railway'
parsed = urlparse(db_url)

conn = pymysql.connect(
    host=parsed.hostname,
    port=parsed.port or 3306,
    user=parsed.username,
    password=parsed.password,
    database=parsed.path.lstrip('/')
)

try:
    cursor = conn.cursor()
    
    email = 'donfabio@360degreesupply.co.za'
    password = 'Dot@com12345'
    password_hash = generate_password_hash(password)
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if not user:
        print(f"Creating user: {email}")
        cursor.execute(
            "INSERT INTO users (email, password_hash, is_admin, created_at) VALUES (%s, %s, TRUE, NOW())",
            (email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        print(f"User created with ID: {user_id}")
    else:
        user_id = user[0]
        print(f"User already exists with ID: {user_id}")
    
    # Create master_admins table
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
    
    # Promote to Master Admin
    cursor.execute("SELECT id FROM master_admins WHERE user_id = %s", (user_id,))
    ma = cursor.fetchone()
    
    if not ma:
        print("Promoting to Master Admin...")
        cursor.execute(
            "INSERT INTO master_admins (user_id, is_active, granted_by, created_at) VALUES (%s, TRUE, %s, NOW())",
            (user_id, user_id)
        )
        conn.commit()
        print("Promoted successfully!")
    else:
        print("Already a Master Admin")
    
    print(f"\nSETUP COMPLETE!")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Access: /master-admin/dashboard")
    
finally:
    cursor.close()
    conn.close()

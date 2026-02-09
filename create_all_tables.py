import pymysql
from urllib.parse import urlparse

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
    
    print("Creating Master Admin tables...")
    
    # 1. master_admins table
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
    print("[OK] master_admins")
    
    # 2. security_events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            event_type VARCHAR(50) NOT NULL,
            description TEXT,
            ip_address VARCHAR(45),
            user_agent VARCHAR(255),
            severity VARCHAR(20) DEFAULT 'low',
            resolved BOOLEAN DEFAULT FALSE,
            resolved_by INT,
            resolved_at DATETIME,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_timestamp (timestamp),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL
        )
    """)
    print("[OK] security_events")
    
    # 3. system_logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            level VARCHAR(20) NOT NULL,
            message TEXT NOT NULL,
            module VARCHAR(100),
            func_name VARCHAR(100),
            line_number INT,
            exception TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_timestamp (timestamp),
            INDEX idx_level (level)
        )
    """)
    print("[OK] system_logs")
    
    # 4. user_activities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activities (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            action VARCHAR(100) NOT NULL,
            details TEXT,
            ip_address VARCHAR(45),
            user_agent VARCHAR(255),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_timestamp (timestamp),
            INDEX idx_user_id (user_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("[OK] user_activities")
    
    conn.commit()
    
    # Promote user to Master Admin
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
    
    print("\n[SUCCESS] All tables created!")
    print("[SUCCESS] User promoted to Master Admin")
    print("\nLogin at: /master-admin/dashboard")
    print("Email: donfabio@360degreesupply.co.za")
    print("Password: Dot@com12345")
    
finally:
    cursor.close()
    conn.close()

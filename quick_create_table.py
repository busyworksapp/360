"""Quick script to create invoice_items table"""
import pymysql
from config import Config
import re

# Parse database URI
uri = Config.SQLALCHEMY_DATABASE_URI
pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
match = re.match(pattern, uri)

if match:
    user, password, host, port, database = match.groups()
    
    conn = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database
    )
    
    cursor = conn.cursor()
    
    try:
        print("Creating invoice_items table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                invoice_id INT NOT NULL,
                order_id INT NULL,
                description VARCHAR(500) NOT NULL,
                quantity INT NOT NULL DEFAULT 1,
                unit_price DECIMAL(10, 2) NOT NULL,
                total DECIMAL(10, 2) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
                INDEX idx_invoice_id (invoice_id),
                INDEX idx_order_id (order_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conn.commit()
        print("✓ invoice_items table created successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
else:
    print("Could not parse database URI")

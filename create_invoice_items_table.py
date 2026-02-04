"""Create invoice_items table for invoice line items"""
from sqlalchemy import create_engine, text
from config import Config

def create_invoice_items_table():
    """Create invoice_items table"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    with engine.connect() as conn:
        print("Creating invoice_items table...")
        try:
            conn.execute(text("""
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
            """))
            conn.commit()
            print("✓ invoice_items table created successfully!")
            return True
        except Exception as e:
            print(f"Error creating table: {e}")
            return False

if __name__ == '____main__':
    print("=== Creating Invoice Items Table ===\n")
    success = create_invoice_items_table()
    if success:
        print("\n✓ Database migration completed!")
        print("You can now create invoices with multiple orders.")
    else:
        print("\n✗ Migration failed. Please check the error messages above.")

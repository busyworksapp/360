"""Fix orders table foreign key constraint to reference customers instead of users"""
from sqlalchemy import create_engine, text
from config import Config

def fix_orders_constraint():
    """Drop old constraint and add new one referencing customers table"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    with engine.connect() as conn:
        print("Dropping old constraint orders_ibfk_1...")
        try:
            conn.execute(text("ALTER TABLE orders DROP FOREIGN KEY orders_ibfk_1"))
            conn.commit()
            print("✓ Old constraint dropped")
        except Exception as e:
            print(f"Note: {e}")
        
        print("\nAdding new constraint referencing customers table...")
        try:
            conn.execute(text("""
                ALTER TABLE orders 
                ADD CONSTRAINT orders_ibfk_1 
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            """))
            conn.commit()
            print("✓ New constraint added successfully!")
        except Exception as e:
            print(f"Error adding constraint: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("=== Fixing Orders Table Constraint ===\n")
    success = fix_orders_constraint()
    if success:
        print("\n✓ Database migration completed!")
        print("You can now proceed with checkout.")
    else:
        print("\n✗ Migration failed. Please check the error messages above.")

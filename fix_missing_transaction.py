"""
Create missing transaction record for Invoice #INV-DE1E6767
"""
import pymysql
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'ballast.proxy.rlwy.net',
    'user': 'root',
    'password': 'VJPYmDrwdrfKuCcGVJffXMyeTLzrkAUo',
    'database': 'railway',
    'port': 14911
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("\n" + "="*70)
    print("FIXING MISSING TRANSACTION FOR INVOICE #INV-DE1E6767")
    print("="*70 + "\n")
    
    # Get invoice and payment details
    cursor.execute("""
        SELECT i.id as invoice_id, i.invoice_number, i.order_id,
               ip.amount, ip.payment_method, ip.payment_date
        FROM invoices i
        JOIN invoice_payments ip ON ip.invoice_id = i.id
        WHERE i.invoice_number = 'INV-DE1E6767'
        ORDER BY ip.payment_date DESC
        LIMIT 1
    """)
    data = cursor.fetchone()
    
    if not data:
        print("❌ Could not find invoice or payment data!")
        exit(1)
    
    if not data['order_id']:
        print("❌ Invoice is not linked to an order!")
        exit(1)
    
    print(f"📄 Invoice: {data['invoice_number']}")
    print(f"📦 Order ID: {data['order_id']}")
    print(f"💰 Payment Amount: R{float(data['amount']):,.2f}")
    print(f"💳 Payment Method: {data['payment_method']}")
    print(f"📅 Payment Date: {data['payment_date']}")
    print()
    
    # Check if transaction already exists
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM transactions
        WHERE order_id = %s
    """, (data['order_id'],))
    existing = cursor.fetchone()
    
    if existing['count'] > 0:
        print(f"⚠️  Transaction already exists for Order ID {data['order_id']}")
        print("   No action needed.")
        exit(0)
    
    # Create the missing transaction
    cursor.execute("""
        INSERT INTO transactions 
        (order_id, amount, payment_method, payment_gateway, status, transaction_date, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['order_id'],
        data['amount'],
        data['payment_method'],
        data['payment_method'],
        'completed',
        data['payment_date'],
        datetime.utcnow(),
        datetime.utcnow()
    ))
    
    transaction_id = cursor.lastrowid
    conn.commit()
    
    print("="*70)
    print("✅ TRANSACTION CREATED SUCCESSFULLY!")
    print("="*70)
    print(f"   Transaction ID: {transaction_id}")
    print(f"   Order ID: {data['order_id']}")
    print(f"   Amount: R{float(data['amount']):,.2f}")
    print(f"   Payment Method: {data['payment_method']}")
    print(f"   Status: completed")
    print(f"   Transaction Date: {data['payment_date']}")
    print("="*70 + "\n")
    
    # Verify the transaction was created
    cursor.execute("""
        SELECT id, amount, payment_method, status
        FROM transactions
        WHERE id = %s
    """, (transaction_id,))
    verification = cursor.fetchone()
    
    if verification:
        print("✅ Verification: Transaction exists in database")
        print(f"   ID: {verification['id']}")
        print(f"   Amount: R{float(verification['amount']):,.2f}")
        print(f"   Method: {verification['payment_method']}")
        print(f"   Status: {verification['status']}")
    else:
        print("❌ Warning: Could not verify transaction creation")
    
    print()
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.rollback()
        conn.close()

import pymysql
from datetime import datetime

conn = pymysql.connect(
    host='ballast.proxy.rlwy.net',
    user='root',
    password='VJPYmDrwdrfKuCcGVJffXMyeTLzrkAUo',
    database='railway',
    port=14911
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

# Get invoice and payment data
cursor.execute('''
    SELECT i.order_id, ip.amount, ip.payment_method, ip.payment_date
    FROM invoices i
    JOIN invoice_payments ip ON ip.invoice_id = i.id
    WHERE i.invoice_number = %s
''', ('INV-DE1E6767',))

data = cursor.fetchone()

if data and data['order_id']:
    # Create transaction
    cursor.execute('''
        INSERT INTO transactions 
        (order_id, amount, currency, payment_method, payment_reference, status, refund_amount, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        data['order_id'],
        data['amount'],
        'ZAR',
        data['payment_method'],
        f"INV-DE1E6767-{data['payment_date'].strftime('%Y%m%d')}",
        'completed',
        0.00,
        datetime.utcnow(),
        datetime.utcnow()
    ))
    
    conn.commit()
    
    print("SUCCESS!")
    print(f"Transaction ID: {cursor.lastrowid}")
    print(f"Order ID: {data['order_id']}")
    print(f"Amount: R{float(data['amount']):,.2f}")
    print(f"Method: {data['payment_method']}")
    print(f"Date: {data['payment_date']}")
else:
    print("ERROR: Could not find invoice or order data")

cursor.close()
conn.close()

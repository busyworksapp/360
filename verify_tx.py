import pymysql

conn = pymysql.connect(
    host='ballast.proxy.rlwy.net',
    user='root',
    password='VJPYmDrwdrfKuCcGVJffXMyeTLzrkAUo',
    database='railway',
    port=14911
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

cursor.execute('SELECT * FROM transactions WHERE order_id = 3')
t = cursor.fetchone()

print("\n" + "="*60)
print("TRANSACTION VERIFICATION")
print("="*60)
print(f"Transaction ID: {t['id']}")
print(f"Order ID: {t['order_id']}")
print(f"Amount: R{float(t['amount']):,.2f}")
print(f"Currency: {t['currency']}")
print(f"Payment Method: {t['payment_method']}")
print(f"Payment Reference: {t['payment_reference']}")
print(f"Status: {t['status']}")
print(f"Refund Amount: R{float(t['refund_amount']):,.2f}")
print(f"Created: {t['created_at']}")
print("="*60 + "\n")

cursor.close()
conn.close()

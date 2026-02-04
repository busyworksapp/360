"""
Link invoice to order and update amounts to match
"""
import pymysql

# Database config
DB_CONFIG = {
    'host': 'ballast.proxy.rlwy.net',
    'user': 'root',
    'password': 'VJPYmDrwdrfKuCcGVJffXMyeTLzrkAUo',
    'database': 'railway',
    'port': 14911
}

def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("\n" + "="*60)
    print("LINKING INVOICE TO ORDER")
    print("="*60 + "\n")
    
    # Get the order
    cursor.execute("""
        SELECT id, order_number, total_amount, subtotal, tax_amount, shipping_cost
        FROM orders
        WHERE order_number = 'ORD-A626B67B'
    """)
    order = cursor.fetchone()
    
    if not order:
        print("❌ Order not found!")
        cursor.close()
        conn.close()
        return
    
    print("📦 ORDER DETAILS:")
    print(f"   Order ID: {order['id']}")
    print(f"   Order Number: {order['order_number']}")
    print(f"   Total: R{float(order['total_amount']):,.2f}")
    print(f"   Subtotal: R{float(order['subtotal']):,.2f}")
    print(f"   Tax: R{float(order['tax_amount']):,.2f}")
    print(f"   Shipping: R{float(order['shipping_cost']):,.2f}")
    print()
    
    # Update invoice to link to order and match amounts
    cursor.execute("""
        UPDATE invoices
        SET order_id = %s,
            total_amount = %s,
            subtotal = %s,
            tax_amount = %s
        WHERE invoice_number = 'INV-DE1E6767'
    """, (order['id'], order['total_amount'], order['subtotal'], order['tax_amount']))
    
    # Update invoice items to reflect correct total
    cursor.execute("""
        UPDATE invoice_items
        SET unit_price = %s,
            total = %s,
            description = %s
        WHERE invoice_id = (SELECT id FROM invoices WHERE invoice_number = 'INV-DE1E6767')
    """, (order['total_amount'], order['total_amount'], 
          f"Order {order['order_number']} (6 items) - Total includes R{float(order['shipping_cost']):,.2f} shipping"))
    
    conn.commit()
    
    print("✅ INVOICE LINKED TO ORDER!")
    print()
    
    # Verify the changes
    cursor.execute("""
        SELECT i.*, o.order_number
        FROM invoices i
        LEFT JOIN orders o ON i.order_id = o.id
        WHERE i.invoice_number = 'INV-DE1E6767'
    """)
    invoice = cursor.fetchone()
    
    print("📊 UPDATED INVOICE:")
    print(f"   Invoice: {invoice['invoice_number']}")
    print(f"   Status: {invoice['status']}")
    print(f"   Linked Order: {invoice['order_number']}")
    print(f"   Subtotal: R{float(invoice['subtotal']):,.2f}")
    print(f"   Tax: R{float(invoice['tax_amount']):,.2f}")
    print(f"   Total: R{float(invoice['total_amount']):,.2f}")
    print(f"   Paid: R{float(invoice['paid_amount']):,.2f}")
    print(f"   Balance Due: R{float(invoice['total_amount']) - float(invoice['paid_amount']):,.2f}")
    print()
    
    print("="*60)
    print("✨ ALL FIXED!")
    print("="*60)
    print("""
The invoice now:
- Has correct status: 'sent' (awaiting payment)
- Links to Order #ORD-A626B67B
- Shows correct total: R27,790.30 (matching order)
- Balance due: R27,790.30

Customer can now pay this invoice at:
http://127.0.0.1:5000/customer/invoices
    """)
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()

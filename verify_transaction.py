"""
Quick script to check transaction for invoice payment
"""
import pymysql

# Database configuration
DB_CONFIG = {
    'host': 'ballast.proxy.rlwy.net',
    'user': 'root',
    'password': 'VJPYmDrwdrfKuCcGVJffXMyeTLzrkAUo',
    'database': 'railway',
    'port': 14911
}

try:
    # Connect to database
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("\n" + "="*70)
    print("TRANSACTION VERIFICATION FOR INVOICE #INV-DE1E6767")
    print("="*70 + "\n")
    
    # Get invoice with linked order
    cursor.execute("""
        SELECT i.id as invoice_id, i.invoice_number, i.order_id, 
               i.total_amount, i.paid_amount, i.status,
               o.order_number, o.payment_status as order_payment_status
        FROM invoices i
        LEFT JOIN orders o ON i.order_id = o.id
        WHERE i.invoice_number = 'INV-DE1E6767'
    """)
    invoice = cursor.fetchone()
    
    if not invoice:
        print("❌ Invoice not found!")
        exit(1)
    
    print("📄 INVOICE DETAILS:")
    print(f"   Invoice Number: {invoice['invoice_number']}")
    print(f"   Status: {invoice['status']}")
    print(f"   Total Amount: R{float(invoice['total_amount']):,.2f}")
    print(f"   Paid Amount: R{float(invoice['paid_amount']):,.2f}")
    balance = float(invoice['total_amount']) - float(invoice['paid_amount'])
    print(f"   Balance: R{balance:,.2f}")
    print()
    
    if invoice['order_id']:
        print("📦 LINKED ORDER:")
        print(f"   Order Number: {invoice['order_number']}")
        print(f"   Payment Status: {invoice['order_payment_status']}")
        print()
    
    # Get invoice payments
    cursor.execute("""
        SELECT id, amount, payment_method, payment_date, status
        FROM invoice_payments
        WHERE invoice_id = %s
        ORDER BY payment_date DESC
    """, (invoice['invoice_id'],))
    payments = cursor.fetchall()
    
    print(f"💳 INVOICE PAYMENTS ({len(payments)} total):")
    if payments:
        for p in payments:
            print(f"   • Payment ID: {p['id']}")
            print(f"     Amount: R{float(p['amount']):,.2f}")
            print(f"     Method: {p['payment_method']}")
            print(f"     Date: {p['payment_date']}")
            print(f"     Status: {p.get('status', 'N/A')}")
            print()
    else:
        print("   ❌ No invoice payments found!")
        print()
    
    # Get order transactions
    if invoice['order_id']:
        cursor.execute("""
            SELECT id, amount, payment_method, payment_gateway, 
                   status, transaction_date, transaction_id
            FROM transactions
            WHERE order_id = %s
            ORDER BY transaction_date DESC
        """, (invoice['order_id'],))
        transactions = cursor.fetchall()
        
        print(f"💰 ORDER TRANSACTIONS ({len(transactions)} total):")
        if transactions:
            for t in transactions:
                print(f"   • Transaction ID: {t['id']}")
                print(f"     Amount: R{float(t['amount']):,.2f}")
                print(f"     Method: {t['payment_method']}")
                print(f"     Gateway: {t['payment_gateway']}")
                print(f"     Status: {t['status']}")
                print(f"     Date: {t['transaction_date']}")
                if t['transaction_id']:
                    print(f"     Gateway Transaction ID: {t['transaction_id']}")
                print()
        else:
            print("   ❌ No transactions found for this order!")
            print()
    
    print("="*70)
    print("SUMMARY:")
    print("="*70)
    print(f"✅ Invoice payment recorded: {len(payments)} payment(s)")
    if invoice['order_id']:
        print(f"{'✅' if len(transactions) > 0 else '❌'} Order transaction recorded: {len(transactions)} transaction(s)")
        
        if len(payments) > 0 and len(transactions) == 0:
            print("\n⚠️  WARNING: Invoice payment exists but order transaction is missing!")
            print("   This means the payment was recorded on the invoice but not on the order.")
            print("   The bug has been fixed in the code, but this payment occurred before the fix.")
    else:
        print("ℹ️  Invoice not linked to an order")
    
    print("="*70 + "\n")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

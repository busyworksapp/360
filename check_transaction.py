"""
Check if transaction was created for the invoice payment
"""
import pymysql

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
    print("CHECKING TRANSACTIONS FOR INVOICE #INV-DE1E6767")
    print("="*60 + "\n")
    
    # Get the invoice and linked order
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
        cursor.close()
        conn.close()
        return
    
    print("📄 INVOICE INFO:")
    print(f"   Invoice: {invoice['invoice_number']}")
    print(f"   Status: {invoice['status']}")
    print(f"   Total: R{float(invoice['total_amount']):,.2f}")
    print(f"   Paid: R{float(invoice['paid_amount']):,.2f}")
    print(f"   Balance: R{float(invoice['total_amount']) - float(invoice['paid_amount']):,.2f}")
    print()
    
    if invoice['order_id']:
        print(f"📦 LINKED ORDER:")
        print(f"   Order: {invoice['order_number']}")
        print(f"   Payment Status: {invoice['order_payment_status']}")
        print()
    
    # Check invoice payments
    cursor.execute("""
        SELECT id, amount, payment_method, payment_date
        FROM invoice_payments
        WHERE invoice_id = %s
        ORDER BY payment_date DESC
    """, (invoice['invoice_id'],))
    invoice_payments = cursor.fetchall()
    
    print(f"💳 INVOICE PAYMENTS ({len(invoice_payments)} total):")
    if invoice_payments:
        for payment in invoice_payments:
            print(f"   • Payment ID: {payment['id']}")
            print(f"     Amount: R{float(payment['amount']):,.2f}")
            print(f"     Method: {payment['payment_method']}")
            print(f"     Date: {payment['payment_date']}")
            print()
    else:
        print("   ❌ No invoice payments found!")
        print()
    
    # Check transactions (if order is linked)
    if invoice['order_id']:
        cursor.execute("""
            SELECT id, amount, payment_method, payment_gateway, 
                   status, transaction_date
            FROM transactions
            WHERE order_id = %s
            ORDER BY transaction_date DESC
        """, (invoice['order_id'],))
        transactions = cursor.fetchall()
        
        print(f"💰 ORDER TRANSACTIONS ({len(transactions)} total):")
        if transactions:
            for txn in transactions:
                print(f"   • Transaction ID: {txn['id']}")
                print(f"     Amount: R{float(txn['amount']):,.2f}")
                print(f"     Method: {txn['payment_method']}")
                print(f"     Gateway: {txn['payment_gateway']}")
                print(f"     Status: {txn['status']}")
                print(f"     Date: {txn['transaction_date']}")
                print()
        else:
            print("   ❌ No transactions found for this order!")
            print()
    
    print("="*60)
    print("SUMMARY:")
    print("="*60)
    
    if invoice_payments:
        print(f"✅ Invoice payment recorded: R{float(invoice_payments[0]['amount']):,.2f}")
    else:
        print("❌ No invoice payment record")
    
    if invoice['order_id']:
        if transactions:
            print(f"✅ Transaction recorded: R{float(transactions[0]['amount']):,.2f}")
        else:
            print("❌ No transaction record (order payment not recorded)")
    
    print()
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()

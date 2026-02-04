"""
Quick verification of invoice fix
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
    
    print("\nVERIFYING INVOICE FIX")
    print("="*60)
    
    # Check invoice
    cursor.execute("""
        SELECT i.invoice_number, i.status, i.total_amount, i.paid_amount,
               i.order_id, o.order_number, o.total_amount as order_total
        FROM invoices i
        LEFT JOIN orders o ON i.order_id = o.id
        WHERE i.invoice_number = 'INV-DE1E6767'
    """)
    invoice = cursor.fetchone()
    
    if invoice:
        balance = float(invoice['total_amount']) - float(invoice['paid_amount'])
        print(f"\nInvoice: {invoice['invoice_number']}")
        print(f"Status: {invoice['status']}")
        print(f"Linked to Order: {invoice['order_number']}")
        print(f"Invoice Total: R{float(invoice['total_amount']):,.2f}")
        print(f"Order Total: R{float(invoice['order_total']):,.2f}")
        print(f"Paid: R{float(invoice['paid_amount']):,.2f}")
        print(f"Balance Due: R{balance:,.2f}")
        
        # Check if amounts match
        if abs(float(invoice['total_amount']) - float(invoice['order_total'])) < 0.01:
            print("\nSTATUS: Invoice and Order amounts MATCH!")
        else:
            print("\nWARNING: Invoice and Order amounts DO NOT MATCH!")
        
        # Check status
        if invoice['status'] == 'sent' and balance > 0:
            print("STATUS: Invoice correctly marked as 'sent' (awaiting payment)")
        elif invoice['status'] == 'paid' and balance == 0:
            print("STATUS: Invoice correctly marked as 'paid'")
        else:
            print(f"WARNING: Status '{invoice['status']}' may not match balance")
    else:
        print("\nERROR: Invoice not found!")
    
    print("\n" + "="*60)
    print("\nCustomer should visit:")
    print("http://127.0.0.1:5000/customer/invoices")
    print("\nTo pay Invoice #INV-DE1E6767")
    print(f"Amount due: R{balance:,.2f}\n")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()

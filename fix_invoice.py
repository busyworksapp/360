"""
Fix invoice #INV-DE1E6767 to match order total and correct status
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
    print("FIXING INVOICE #INV-DE1E6767")
    print("="*60 + "\n")
    
    # Get current invoice data
    cursor.execute("""
        SELECT i.*, o.total_amount as order_total, o.subtotal as order_subtotal,
               o.tax_amount as order_tax, o.shipping_cost as order_shipping
        FROM invoices i
        LEFT JOIN orders o ON i.order_id = o.id
        WHERE i.invoice_number = 'INV-DE1E6767'
    """)
    invoice = cursor.fetchone()
    
    if not invoice:
        print("❌ Invoice #INV-DE1E6767 not found!")
        cursor.close()
        conn.close()
        return
    
    print("📋 CURRENT INVOICE STATE:")
    print(f"   Invoice ID: {invoice['id']}")
    print(f"   Status: {invoice['status']}")
    print(f"   Total: R{float(invoice['total_amount']):,.2f}")
    print(f"   Paid: R{float(invoice['paid_amount']):,.2f}")
    print(f"   Order ID: {invoice['order_id']}")
    if invoice['order_total']:
        print(f"   Order Total: R{float(invoice['order_total']):,.2f}")
    print()
    
    # Determine correct values
    if invoice['order_total']:
        correct_total = float(invoice['order_total'])
        correct_subtotal = float(invoice['order_subtotal']) if invoice['order_subtotal'] else 0
        correct_tax = float(invoice['order_tax']) if invoice['order_tax'] else 0
    else:
        # No linked order, keep current values
        correct_total = float(invoice['total_amount'])
        correct_subtotal = float(invoice['subtotal']) if invoice['subtotal'] else 0
        correct_tax = float(invoice['tax_amount']) if invoice['tax_amount'] else 0
    
    # Determine correct status
    if float(invoice['paid_amount']) >= correct_total:
        correct_status = 'paid'
    elif float(invoice['paid_amount']) > 0:
        correct_status = 'partial'
    else:
        # Not paid yet, change from 'paid' to 'sent' (invoice has been sent to customer)
        correct_status = 'sent'
    
    print("✨ CORRECTIONS TO APPLY:")
    print(f"   Status: {invoice['status']} → {correct_status}")
    print(f"   Total: R{float(invoice['total_amount']):,.2f} → R{correct_total:,.2f}")
    print(f"   Subtotal: R{float(invoice['subtotal']):,.2f} → R{correct_subtotal:,.2f}")
    print(f"   Tax: R{float(invoice['tax_amount']):,.2f} → R{correct_tax:,.2f}")
    print()
    
    # Update invoice
    cursor.execute("""
        UPDATE invoices
        SET status = %s,
            total_amount = %s,
            subtotal = %s,
            tax_amount = %s
        WHERE id = %s
    """, (correct_status, correct_total, correct_subtotal, correct_tax, invoice['id']))
    
    # Also update invoice items to reflect correct total
    cursor.execute("""
        UPDATE invoice_items
        SET unit_price = %s,
            total = %s
        WHERE invoice_id = %s
    """, (correct_total, correct_total, invoice['id']))
    
    conn.commit()
    
    print("✅ INVOICE UPDATED SUCCESSFULLY!")
    print()
    print("📊 VERIFICATION:")
    
    # Verify the changes
    cursor.execute("""
        SELECT status, total_amount, subtotal, tax_amount, paid_amount
        FROM invoices
        WHERE id = %s
    """, (invoice['id'],))
    updated = cursor.fetchone()
    
    print(f"   Status: {updated['status']}")
    print(f"   Total: R{float(updated['total_amount']):,.2f}")
    print(f"   Subtotal: R{float(updated['subtotal']):,.2f}")
    print(f"   Tax: R{float(updated['tax_amount']):,.2f}")
    print(f"   Paid: R{float(updated['paid_amount']):,.2f}")
    print(f"   Balance: R{float(updated['total_amount']) - float(updated['paid_amount']):,.2f}")
    print()
    
    print("="*60)
    print("NEXT STEPS FOR CUSTOMER:")
    print("="*60)
    print("""
1. Customer should log in at: http://127.0.0.1:5000/customer/login
2. Navigate to "My Invoices"
3. View Invoice #INV-DE1E6767
4. Pay the invoice using the payment button
5. Amount due: R27,790.30
    """)
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()

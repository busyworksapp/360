"""
Quick diagnostic script to check customer cart and order data
"""
import pymysql
from decimal import Decimal

# Database config
DB_CONFIG = {
    'host': 'ballast.proxy.rlwy.net',
    'user': 'root',
    'password': 'VJPYmDrwdrfKuCcGVJffXMyeTLzrkAUo',
    'database': 'railway',
    'port': 14911
}

def format_amount(amount):
    """Format amount as currency"""
    if amount is None:
        return "R0.00"
    return f"R{float(amount):,.2f}"

def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("\n" + "="*60)
    print("CUSTOMER CART & ORDER INSPECTION")
    print("="*60 + "\n")
    
    # Get all customers
    cursor.execute("SELECT id, first_name, last_name, email, company FROM customers ORDER BY id")
    customers = cursor.fetchall()
    
    for customer in customers:
        full_name = f"{customer['first_name'] or ''} {customer['last_name'] or ''}".strip() or "No Name"
        print("─"*60)
        print(f"👤 CUSTOMER: {full_name} (ID: {customer['id']})")
        print(f"   Email: {customer['email']}")
        if customer['company']:
            print(f"   Company: {customer['company']}")
        print("─"*60)
        
        # Get carts
        cursor.execute("""
            SELECT c.id, c.is_active, 
                   COALESCE(SUM(ci.quantity * p.price), 0) as subtotal,
                   COUNT(ci.id) as item_count
            FROM carts c
            LEFT JOIN cart_items ci ON c.id = ci.cart_id
            LEFT JOIN products p ON ci.product_id = p.id
            WHERE c.customer_id = %s
            GROUP BY c.id, c.is_active
            ORDER BY c.is_active DESC, c.id DESC
        """, (customer['id'],))
        carts = cursor.fetchall()
        
        print(f"\n📦 CARTS ({len(carts)} total):")
        if carts:
            for cart in carts:
                status = "🟢 ACTIVE" if cart['is_active'] else "⚫ INACTIVE"
                print(f"   Cart ID {cart['id']}: {status}")
                print(f"   - Items: {cart['item_count']}")
                print(f"   - Subtotal: {format_amount(cart['subtotal'])}")
                
                # Get cart items
                if cart['item_count'] > 0:
                    cursor.execute("""
                        SELECT p.name, ci.quantity, p.price
                        FROM cart_items ci
                        JOIN products p ON ci.product_id = p.id
                        WHERE ci.cart_id = %s
                    """, (cart['id'],))
                    items = cursor.fetchall()
                    for item in items:
                        print(f"     • {item['name']} (Qty: {item['quantity']}) - {format_amount(item['price'])} each")
                print()
        else:
            print("   No carts found")
        
        # Get orders
        cursor.execute("""
            SELECT o.id, o.order_number, o.status, o.payment_status, 
                   o.subtotal, o.tax_amount, o.shipping_cost, o.total_amount,
                   o.created_at, COUNT(oi.id) as item_count
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.customer_id = %s
            GROUP BY o.id
            ORDER BY o.created_at DESC
        """, (customer['id'],))
        orders = cursor.fetchall()
        
        print(f"📋 ORDERS ({len(orders)} total):")
        if orders:
            for order in orders:
                print(f"   Order #{order['order_number']}")
                print(f"   - Status: {order['status']}")
                print(f"   - Payment: {order['payment_status']}")
                print(f"   - Items: {order['item_count']}")
                print(f"   - Subtotal: {format_amount(order['subtotal'])}")
                print(f"   - Tax: {format_amount(order['tax_amount'])}")
                print(f"   - Shipping: {format_amount(order['shipping_cost'])}")
                print(f"   - Total: {format_amount(order['total_amount'])}")
                print(f"   - Created: {order['created_at']}")
                
                # Check for the specific amount
                total = float(order['total_amount']) if order['total_amount'] else 0
                if abs(total - 27690.27) < 1:
                    print(f"   ⭐ FOUND: This order matches R27,690.27!")
                
                # Get order items
                cursor.execute("""
                    SELECT p.name, oi.quantity, oi.price_at_purchase
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = %s
                """, (order['id'],))
                items = cursor.fetchall()
                if items:
                    print(f"   Items:")
                    for item in items:
                        item_total = item['quantity'] * item['price_at_purchase']
                        print(f"     • {item['name']} (Qty: {item['quantity']}) - {format_amount(item['price_at_purchase'])} each = {format_amount(item_total)}")
                print()
        else:
            print("   No orders found")
        
        # Get invoices
        cursor.execute("""
            SELECT i.id, i.invoice_number, i.status, i.total_amount, 
                   i.paid_amount, i.due_date, i.issue_date
            FROM invoices i
            WHERE i.customer_id = %s
            ORDER BY i.issue_date DESC
        """, (customer['id'],))
        invoices = cursor.fetchall()
        
        print(f"💰 INVOICES ({len(invoices)} total):")
        if invoices:
            for invoice in invoices:
                balance = float(invoice['total_amount']) - float(invoice['paid_amount']) if invoice['total_amount'] and invoice['paid_amount'] else float(invoice['total_amount']) if invoice['total_amount'] else 0
                print(f"   📄 Invoice #{invoice['invoice_number']}")
                print(f"   - Status: {invoice['status']}")
                print(f"   - Total: {format_amount(invoice['total_amount'])}")
                print(f"   - Paid: {format_amount(invoice['paid_amount'])}")
                print(f"   - Balance: {format_amount(balance)}")
                print(f"   - Issue Date: {invoice['issue_date']}")
                print(f"   - Due Date: {invoice['due_date']}")
                
                # Check for the specific amount
                total = float(invoice['total_amount']) if invoice['total_amount'] else 0
                if abs(total - 27690.27) < 1 or abs(balance - 27690.27) < 1:
                    print(f"   ⭐ FOUND: This invoice matches R27,690.27!")
                
                # Get invoice items
                cursor.execute("""
                    SELECT ii.description, ii.quantity, ii.unit_price, ii.total,
                           o.order_number
                    FROM invoice_items ii
                    LEFT JOIN orders o ON ii.order_id = o.id
                    WHERE ii.invoice_id = %s
                """, (invoice['id'],))
                items = cursor.fetchall()
                if items:
                    print(f"   Items:")
                    for item in items:
                        order_ref = f" [Order {item['order_number']}]" if item['order_number'] else ""
                        print(f"     • {item['description']}{order_ref}")
                        print(f"       Qty: {item['quantity']} × {format_amount(item['unit_price'])} = {format_amount(item['total'])}")
                print()
        else:
            print("   No invoices found")
        
        print()
    
    # Search for the specific amount
    print("\n" + "="*60)
    print("DIAGNOSIS: SEARCHING FOR R27,690.27")
    print("="*60)
    
    # Check orders
    cursor.execute("""
        SELECT o.id, o.order_number, o.total_amount, c.first_name, c.last_name, c.email
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE ABS(o.total_amount - 27690.27) < 1
    """)
    matching_orders = cursor.fetchall()
    
    if matching_orders:
        print(f"\n✅ Found {len(matching_orders)} order(s) matching R27,690.27:")
        for order in matching_orders:
            full_name = f"{order['first_name'] or ''} {order['last_name'] or ''}".strip() or "No Name"
            print(f"   • Order #{order['order_number']} - {format_amount(order['total_amount'])}")
            print(f"     Customer: {full_name} ({order['email']})")
            print(f"     → Customer should view order at: http://127.0.0.1:5000/customer/orders")
    
    # Check invoices
    cursor.execute("""
        SELECT i.id, i.invoice_number, i.total_amount, i.paid_amount, 
               c.first_name, c.last_name, c.email
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        WHERE ABS(i.total_amount - 27690.27) < 1 
           OR ABS(i.total_amount - i.paid_amount - 27690.27) < 1
    """)
    matching_invoices = cursor.fetchall()
    
    if matching_invoices:
        print(f"\n✅ Found {len(matching_invoices)} invoice(s) matching R27,690.27:")
        for invoice in matching_invoices:
            full_name = f"{invoice['first_name'] or ''} {invoice['last_name'] or ''}".strip() or "No Name"
            balance = float(invoice['total_amount']) - float(invoice['paid_amount']) if invoice['total_amount'] and invoice['paid_amount'] else float(invoice['total_amount']) if invoice['total_amount'] else 0
            print(f"   • Invoice #{invoice['invoice_number']} - {format_amount(invoice['total_amount'])}")
            print(f"     Balance: {format_amount(balance)}")
            print(f"     Customer: {full_name} ({invoice['email']})")
            print(f"     → Customer should pay invoice at: http://127.0.0.1:5000/customer/invoices")
    
    if not matching_orders and not matching_invoices:
        print("\n❌ No orders or invoices found matching R27,690.27")
        print("   The amount might be from a cached cart or UI bug")
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    print("""
If cart is empty but amount shows:
1. This is EXPECTED after checkout - cart clears when order is created
2. Customer should navigate to "My Orders" to view their order
3. Customer should navigate to "My Invoices" to pay any invoices
4. If no order/invoice exists, clear browser cache and refresh

The "Cart is empty" message is correct - the R27,690.27 is from
a completed order or pending invoice, not the current cart.
    """)
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()

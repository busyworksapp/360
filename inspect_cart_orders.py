"""Inspect customer carts, orders, and invoices to diagnose empty cart issue"""
from app import app, db
from models import Customer, Cart, CartItem, Order, OrderItem, Invoice

with app.app_context():
    print("\n" + "="*80)
    print("CUSTOMER CART & ORDER INSPECTION")
    print("="*80 + "\n")
    
    customers = Customer.query.all()
    
    if not customers:
        print("❌ No customers found in database")
        exit()
    
    for customer in customers:
        print(f"\n{'─'*80}")
        print(f"👤 CUSTOMER: {customer.get_full_name()} (ID: {customer.id})")
        print(f"   Email: {customer.email}")
        print(f"   Company: {customer.company or 'N/A'}")
        print(f"{'─'*80}")
        
        # Check carts
        carts = Cart.query.filter_by(customer_id=customer.id).all()
        print(f"\n📦 CARTS ({len(carts)} total):")
        
        if carts:
            for cart in carts:
                status = "🟢 ACTIVE" if cart.is_active else "⚫ INACTIVE"
                item_count = len(cart.items) if cart.items else 0
                subtotal = cart.get_subtotal() if cart.is_active and cart.items else 0
                
                print(f"   Cart ID {cart.id}: {status}")
                print(f"   - Items: {item_count}")
                print(f"   - Subtotal: R{subtotal:.2f}")
                
                if cart.items:
                    for item in cart.items:
                        print(f"     • {item.product.name if item.product else 'Product deleted'} x{item.quantity} @ R{item.price_at_add:.2f}")
        else:
            print("   No carts found")
        
        # Check orders
        orders = Order.query.filter_by(customer_id=customer.id).order_by(Order.created_at.desc()).all()
        print(f"\n📋 ORDERS ({len(orders)} total):")
        
        if orders:
            for order in orders:
                print(f"   Order #{order.order_number}")
                print(f"   - Status: {order.status}")
                print(f"   - Payment: {order.payment_status}")
                print(f"   - Total: R{order.total_amount:.2f} (Subtotal: R{order.subtotal:.2f} + Tax: R{order.tax_amount:.2f} + Shipping: R{order.shipping_cost:.2f})")
                print(f"   - Items: {len(order.items)}")
                print(f"   - Created: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if order.items:
                    for item in order.items:
                        print(f"     • {item.product.name if item.product else 'Product deleted'} x{item.quantity} @ R{item.price_at_purchase:.2f}")
                print()
        else:
            print("   No orders found")
        
        # Check invoices
        invoices = Invoice.query.filter_by(customer_id=customer.id).order_by(Invoice.issue_date.desc()).all()
        print(f"💰 INVOICES ({len(invoices)} total):")
        
        if invoices:
            for invoice in invoices:
                balance = invoice.remaining_balance()
                status_icon = "✅" if invoice.status == 'paid' else "⏳" if invoice.status == 'partial' else "❌" if invoice.is_overdue() else "📄"
                
                print(f"   {status_icon} Invoice #{invoice.invoice_number}")
                print(f"   - Status: {invoice.status}")
                print(f"   - Total: R{invoice.total_amount:.2f}")
                print(f"   - Paid: R{invoice.paid_amount:.2f}")
                print(f"   - Balance: R{balance:.2f}")
                print(f"   - Due: {invoice.due_date.strftime('%Y-%m-%d')}")
                print(f"   - Items: {len(invoice.items) if invoice.items else 0}")
                
                if invoice.items:
                    for item in invoice.items:
                        print(f"     • {item.description} x{item.quantity} @ R{item.unit_price:.2f} = R{item.total:.2f}")
                print()
        else:
            print("   No invoices found")
        
        print()
    
    print("\n" + "="*80)
    print("DIAGNOSIS & RECOMMENDATIONS")
    print("="*80)
    
    # Find the R27,690.27 amount
    target_amount = 27690.27
    found_orders = Order.query.filter(
        (Order.total_amount >= target_amount - 1) & 
        (Order.total_amount <= target_amount + 1)
    ).all()
    
    found_invoices = Invoice.query.filter(
        (Invoice.total_amount >= target_amount - 1) & 
        (Invoice.total_amount <= target_amount + 1)
    ).all()
    
    if found_orders:
        print(f"\n🔍 Found {len(found_orders)} order(s) matching R{target_amount:.2f}:")
        for order in found_orders:
            customer = Customer.query.get(order.customer_id)
            print(f"   • Order #{order.order_number} for {customer.get_full_name()}")
            print(f"     Status: {order.status} | Payment: {order.payment_status}")
            
            # Check if cart is empty
            active_cart = Cart.query.filter_by(customer_id=order.customer_id, is_active=True).first()
            if not active_cart or not active_cart.items:
                print(f"     ✅ EXPECTED: Cart is empty (order was placed, cart cleared)")
                print(f"     → Customer should view order at: /customer/orders")
            else:
                print(f"     ⚠️ UNEXPECTED: Customer has active cart with {len(active_cart.items)} items")
    
    if found_invoices:
        print(f"\n🔍 Found {len(found_invoices)} invoice(s) matching R{target_amount:.2f}:")
        for invoice in found_invoices:
            customer = Customer.query.get(invoice.customer_id)
            balance = invoice.remaining_balance()
            print(f"   • Invoice #{invoice.invoice_number} for {customer.get_full_name()}")
            print(f"     Status: {invoice.status} | Balance: R{balance:.2f}")
            print(f"     → Customer should pay at: /customer/invoices/{invoice.id}")
    
    if not found_orders and not found_invoices:
        print(f"\n⚠️ No orders or invoices found matching R{target_amount:.2f}")
        print("   The amount may be showing from:")
        print("   - A previous session's cart (browser cache)")
        print("   - An incomplete checkout")
        print("   - A different amount (check all orders/invoices above)")
    
    print("\n" + "="*80)

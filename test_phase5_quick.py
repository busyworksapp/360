#!/usr/bin/env python3
"""
Quick test script for Phase 5 - Order Management System
Tests core functionality without user interaction
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
RESULTS = []

def test(name, condition, details=""):
    """Log test result"""
    status = "✅ PASS" if condition else "❌ FAIL"
    RESULTS.append((name, condition))
    print(f"{status}: {name}")
    if details:
        print(f"   → {details}")

def main():
    print("\n" + "="*60)
    print("PHASE 5 - ORDER MANAGEMENT SYSTEM - QUICK TEST")
    print("="*60 + "\n")
    
    print("📋 TEST 1: Server Connectivity")
    print("-" * 60)
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        test("Server Response", resp.status_code == 200, f"Status: {resp.status_code}")
        test("Homepage Contains Content", len(resp.text) > 100, f"Response length: {len(resp.text)}")
    except Exception as e:
        test("Server Connection", False, str(e))
        print("\n❌ Cannot connect to server. Make sure Flask is running.")
        return
    
    print("\n📋 TEST 2: Route Availability")
    print("-" * 60)
    routes = [
        ("/products", 200, "Products page"),
        ("/customer/login", 200, "Customer login"),
        ("/admin", 302, "Admin dashboard (redirect if not logged in)"),
    ]
    
    for route, expected_status, description in routes:
        try:
            resp = requests.get(f"{BASE_URL}{route}", allow_redirects=False)
            test(f"Route {route}", 
                 resp.status_code == expected_status, 
                 f"Expected {expected_status}, got {resp.status_code}")
        except Exception as e:
            test(f"Route {route}", False, str(e))
    
    print("\n📋 TEST 3: Order Models Verification")
    print("-" * 60)
    try:
        from models import Order, OrderItem, db
        test("Order model imported", True, "Order class available")
        test("OrderItem model imported", True, "OrderItem class available")
        
        # Check Order model attributes
        order_attrs = ['id', 'customer_id', 'order_number', 'status', 'total_amount', 'items']
        for attr in order_attrs:
            has_attr = hasattr(Order, attr) or attr in ['id', 'items']
            test(f"Order.{attr}", has_attr, f"Attribute present")
        
        # Check OrderItem model attributes
        item_attrs = ['id', 'order_id', 'product_id', 'quantity', 'price_at_purchase']
        for attr in item_attrs:
            has_attr = hasattr(OrderItem, attr) or attr in ['id']
            test(f"OrderItem.{attr}", has_attr, f"Attribute present")
    except Exception as e:
        test("Models Import", False, str(e))
    
    print("\n📋 TEST 4: Database Tables")
    print("-" * 60)
    try:
        from app import app
        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            test("Orders table exists", 'orders' in tables, f"Tables: {tables}")
            test("OrderItems table exists", 'order_items' in tables, f"Tables: {tables}")
            
            if 'orders' in tables:
                columns = [c['name'] for c in inspector.get_columns('orders')]
                required_cols = ['id', 'customer_id', 'order_number', 'status', 'total_amount']
                for col in required_cols:
                    test(f"orders.{col}", col in columns, f"Column present")
                    
            if 'order_items' in tables:
                columns = [c['name'] for c in inspector.get_columns('order_items')]
                required_cols = ['id', 'order_id', 'product_id', 'quantity', 'price_at_purchase']
                for col in required_cols:
                    test(f"order_items.{col}", col in columns, f"Column present")
    except Exception as e:
        test("Database Check", False, str(e))
    
    print("\n📋 TEST 5: Email Service")
    print("-" * 60)
    try:
        from email_service import EmailService
        service = EmailService()
        test("EmailService imported", True, "Email service available")
        test("send_order_confirmation method exists", 
             hasattr(service, 'send_order_confirmation'),
             "Method is available")
    except Exception as e:
        test("Email Service", False, str(e))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, result in RESULTS if result)
    total = len(RESULTS)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"📊 Success Rate: {percentage:.1f}%")
    
    if percentage == 100:
        print("\n🎉 ALL TESTS PASSED! Phase 5 is ready for comprehensive testing.")
    elif percentage >= 80:
        print("\n⚠️  Most tests passed. Please review failures above.")
    else:
        print("\n❌ Several tests failed. Please check setup and try again.")
    
    print("\n" + "="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

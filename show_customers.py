"""Show customer login credentials"""
from app import app, db
from models import Customer

with app.app_context():
    customers = Customer.query.all()
    
    print("\n=== Customer Accounts ===\n")
    
    if not customers:
        print("No customer accounts found in database.")
        print("\nYou can register a new customer at:")
        print("http://127.0.0.1:5000/customer/register")
    else:
        print(f"Found {len(customers)} customer account(s):\n")
        for customer in customers:
            print(f"ID: {customer.id}")
            print(f"Name: {customer.get_full_name()}")
            print(f"Email: {customer.email}")
            print(f"Company: {customer.company or 'N/A'}")
            print(f"Active: {customer.is_active}")
            print("-" * 50)
        
        print("\nNOTE: Customer passwords are hashed and cannot be displayed.")
        print("If you don't know the password, you can:")
        print("1. Register a new customer at: http://127.0.0.1:5000/customer/register")
        print("2. Or use the test customer email shown above with password you set during registration")

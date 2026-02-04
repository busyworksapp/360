from app import app, db
from models import Customer
from werkzeug.security import generate_password_hash

def create_customer():
    with app.app_context():
        # Check if customer already exists
        existing = Customer.query.filter_by(email='customer@360degreesupply.co.za').first()
        if existing:
            print("Customer already exists!")
            print(f"Email: customer@360degreesupply.co.za")
            print(f"Password: customer123")
            return
        
        # Create new customer
        customer = Customer(
            first_name='John',
            last_name='Doe',
            email='customer@360degreesupply.co.za',
            phone='+27123456789',
            company='Test Company',
            address='123 Test Street',
            city='Johannesburg',
            postal_code='2000',
            country='South Africa',
            is_active=True
        )
        customer.set_password('customer123')
        
        db.session.add(customer)
        db.session.commit()
        
        print("✅ Customer created successfully!")
        print("=" * 50)
        print("Customer Login Credentials:")
        print("=" * 50)
        print(f"Email: customer@360degreesupply.co.za")
        print(f"Password: customer123")
        print("=" * 50)
        print(f"Name: {customer.first_name} {customer.last_name}")
        print(f"Company: {customer.company}")
        print(f"Phone: {customer.phone}")
        print("=" * 50)

if __name__ == '__main__':
    create_customer()

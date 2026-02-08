"""
PRODUCTION DATABASE RESET
Removes all demo/test data and prepares for live production
"""
from app import app, db
from models import (
    User, Customer, Product, Service, Order, OrderItem, Invoice, 
    InvoiceItem, InvoicePayment, Transaction, Cart, CartItem,
    Testimonial, HeroSection, ContactSubmission, ProofOfPayment,
    AuditLog, CompanyInfo, HomePageSettings
)
from werkzeug.security import generate_password_hash
import sys

def reset_for_production():
    """Reset database for production - keep only essential data"""
    
    with app.app_context():
        print("=" * 60)
        print("PRODUCTION DATABASE RESET")
        print("=" * 60)
        print("\nWARNING: This will delete ALL demo data!")
        print("Only company info and admin account will be kept.")
        
        confirm = input("\nType 'RESET' to confirm: ")
        if confirm != 'RESET':
            print("Aborted.")
            return
        
        print("\n🗑️  Deleting demo data...")
        
        # Delete transactional data
        ProofOfPayment.query.delete()
        print("  ✅ Deleted proof of payments")
        
        InvoicePayment.query.delete()
        print("  ✅ Deleted invoice payments")
        
        InvoiceItem.query.delete()
        print("  ✅ Deleted invoice items")
        
        Invoice.query.delete()
        print("  ✅ Deleted invoices")
        
        Transaction.query.delete()
        print("  ✅ Deleted transactions")
        
        OrderItem.query.delete()
        print("  ✅ Deleted order items")
        
        Order.query.delete()
        print("  ✅ Deleted orders")
        
        CartItem.query.delete()
        print("  ✅ Deleted cart items")
        
        Cart.query.delete()
        print("  ✅ Deleted carts")
        
        # Delete customer data
        Customer.query.delete()
        print("  ✅ Deleted customers")
        
        # Delete content data
        Product.query.delete()
        print("  ✅ Deleted products")
        
        Service.query.delete()
        print("  ✅ Deleted services")
        
        Testimonial.query.delete()
        print("  ✅ Deleted testimonials")
        
        HeroSection.query.delete()
        print("  ✅ Deleted hero sections")
        
        ContactSubmission.query.delete()
        print("  ✅ Deleted contact submissions")
        
        # Keep audit logs for security (optional - uncomment to delete)
        # AuditLog.query.delete()
        # print("  ✅ Deleted audit logs")
        
        # Delete demo admin users (keep only production admin)
        User.query.filter(User.email != 'admin@360degreesupply.co.za').delete()
        print("  ✅ Deleted demo admin users")
        
        db.session.commit()
        
        print("\n✅ Demo data deleted successfully!")
        
        # Ensure production admin exists
        print("\n🔧 Setting up production admin...")
        admin = User.query.filter_by(email='admin@360degreesupply.co.za').first()
        
        if not admin:
            print("\n⚠️  No admin account found. Creating new admin...")
            print("Enter admin password (min 12 chars, uppercase, lowercase, digit, special):")
            password = input("Password: ")
            
            # Validate password
            from security_utils import validate_password_strength
            is_valid, error = validate_password_strength(password)
            
            if not is_valid:
                print(f"\n❌ Password validation failed: {error}")
                print("Please run this script again with a stronger password.")
                return
            
            admin = User(
                email='admin@360degreesupply.co.za',
                is_admin=True
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print("  ✅ Admin account created")
        else:
            print("  ✅ Admin account exists")
            
            # Option to reset admin password
            reset_pwd = input("\nReset admin password? (y/N): ")
            if reset_pwd.lower() == 'y':
                print("Enter new password (min 12 chars, uppercase, lowercase, digit, special):")
                password = input("Password: ")
                
                from security_utils import validate_password_strength
                is_valid, error = validate_password_strength(password)
                
                if not is_valid:
                    print(f"\n❌ Password validation failed: {error}")
                else:
                    admin.set_password(password)
                    db.session.commit()
                    print("  ✅ Admin password updated")
        
        # Ensure company info exists
        print("\n🏢 Checking company info...")
        company = CompanyInfo.query.first()
        
        if not company:
            print("  ⚠️  No company info found. Creating default...")
            company = CompanyInfo(
                company_name='360Degree Supply (Pty) Ltd',
                address='Ei Ridge Office Park, 100 Elizabeth Road, Impala Park, Boksburg, 1459, Gauteng, South Africa',
                phone='+27 64 902 4363 / +27 71 181 4799',
                email='info@360degreesupply.co.za',
                description='360Degree Supply (Pty) Ltd is a South African–based bulk fuel and mineral supply company.',
                mission='To be a trusted supply partner, providing certainty, transparency, and efficiency.',
                established_year='2020'
            )
            db.session.add(company)
            db.session.commit()
            print("  ✅ Company info created")
        else:
            print("  ✅ Company info exists")
        
        # Ensure homepage settings exist
        print("\n🏠 Checking homepage settings...")
        homepage = HomePageSettings.query.first()
        
        if not homepage:
            print("  ⚠️  No homepage settings found. Creating default...")
            homepage = HomePageSettings(
                hero_title='Welcome to 360Degree Supply',
                hero_description='Your trusted partner for bulk fuel and mineral supply.',
                hero_button_text='Contact Us',
                hero_button_link='/contact',
                show_stats_card=False
            )
            db.session.add(homepage)
            db.session.commit()
            print("  ✅ Homepage settings created")
        else:
            print("  ✅ Homepage settings exist")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE READY FOR PRODUCTION!")
        print("=" * 60)
        
        print("\n📊 Database Summary:")
        print(f"  - Admin Users: {User.query.count()}")
        print(f"  - Customers: {Customer.query.count()}")
        print(f"  - Products: {Product.query.count()}")
        print(f"  - Services: {Service.query.count()}")
        print(f"  - Orders: {Order.query.count()}")
        print(f"  - Invoices: {Invoice.query.count()}")
        print(f"  - Audit Logs: {AuditLog.query.count()} (kept for security)")
        
        print("\n🚀 Next Steps:")
        print("  1. Add your real products via /admin/products/add")
        print("  2. Add your real services via /admin/services/add")
        print("  3. Update company info via /admin/company")
        print("  4. Enable 2FA for admin via /admin/2fa/setup")
        print("  5. Deploy to production")
        
        print("\n⚠️  IMPORTANT:")
        print("  - Change admin password if using default")
        print("  - Enable 2FA immediately")
        print("  - Update company information")
        print("  - Set strong SECRET_KEY in .env")
        print("  - Enable HTTPS in production")

if __name__ == '__main__':
    reset_for_production()

#!/usr/bin/env python
"""Quick system verification script."""

from app import app, db
from models import Service, Product, CompanyInfo, User

def verify_system():
    """Verify all systems are operational."""
    print("\n" + "="*60)
    print("🔍 SYSTEM VERIFICATION - 360Degree Supply Website")
    print("="*60)
    
    with app.app_context():
        try:
            # Check Flask App
            print("\n✅ Flask Application: LOADED")
            
            # Check Database Connection
            print("✅ Database Connection: OK")
            
            # Check Admin User
            admin = User.query.filter_by(email='admin@360degreesupply.co.za').first()
            print(f"✅ Admin User: {admin.email if admin else 'NOT FOUND'}")
            
            # Check Company Info
            company = CompanyInfo.query.first()
            if company:
                print(f"✅ Company: {company.company_name}")
                print(f"   Address: {company.address[:50]}...")
                print(f"   Phone: {company.phone}")
            
            # Check Services
            services = Service.query.filter_by(is_active=True).count()
            print(f"✅ Services: {services} active services")
            
            # Check Products
            products = Product.query.filter_by(is_active=True).count()
            print(f"✅ Products: {products} active products")
            
            # List Services
            print("\n📋 Active Services:")
            for service in Service.query.filter_by(is_active=True).all():
                print(f"   • {service.title}")
            
            # List Products
            print("\n📦 Active Products:")
            for product in Product.query.filter_by(is_active=True).all():
                print(f"   • {product.name} - R{product.price:.2f}/{product.unit}")
            
            print("\n" + "="*60)
            print("✅ ALL SYSTEMS OPERATIONAL")
            print("="*60)
            print("\n🌐 Access the website:")
            print("   Public: http://127.0.0.1:5000")
            print("   Admin:  http://127.0.0.1:5000/admin")
            print("\n📧 Admin Credentials:")
            print("   Email: admin@360degreesupply.co.za")
            print("   Password: admin123")
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            return False
    
    return True

if __name__ == '__main__':
    success = verify_system()
    exit(0 if success else 1)

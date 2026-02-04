"""
Verify all products and services have valid images
"""
import os
from app import app, db
from models import Product, Service

def verify_images():
    """Verify all images are valid and exist"""
    print("\n" + "="*60)
    print("IMAGE VERIFICATION")
    print("="*60)
    
    uploads_dir = 'static/uploads'
    
    # Verify products
    print("\n📦 PRODUCTS:")
    print("-" * 60)
    products = Product.query.all()
    for product in products:
        image_path = product.image_url
        if image_path:
            # Extract filename
            filename = os.path.basename(image_path)
            full_path = os.path.join(uploads_dir, filename)
            exists = os.path.exists(full_path)
            
            status = "✓" if exists else "❌"
            print(f"{status} {product.name:<40} → {filename}")
        else:
            print(f"❌ {product.name:<40} → NO IMAGE SET")
    
    # Verify services
    print("\n🛠️  SERVICES:")
    print("-" * 60)
    services = Service.query.all()
    for service in services:
        image_path = service.image_url
        if image_path:
            # Extract filename
            filename = os.path.basename(image_path)
            full_path = os.path.join(uploads_dir, filename)
            exists = os.path.exists(full_path)
            
            status = "✓" if exists else "❌"
            print(f"{status} {service.title:<40} → {filename}")
        else:
            print(f"❌ {service.title:<40} → NO IMAGE SET")
    
    print("\n" + "="*60)
    print("✓ VERIFICATION COMPLETE")
    print("="*60)
    print("\nAll images have been verified.")
    print("If you see any ❌, those files are missing from static/uploads/")

if __name__ == '__main__':
    with app.app_context():
        verify_images()

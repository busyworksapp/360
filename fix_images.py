"""
Fix missing images by updating database references to use available images
"""
import os
from app import app, db
from models import Product, Service
from sqlalchemy import text

def check_image_exists(image_path):
    """Check if image file exists"""
    if not image_path:
        return False
    
    # Remove leading slash and /static/ prefix if present
    clean_path = image_path.strip('/')
    if clean_path.startswith('static/'):
        clean_path = clean_path[7:]  # Remove 'static/' prefix
    
    # Check in static/uploads directory
    full_path = os.path.join('static', 'uploads', os.path.basename(clean_path))
    exists = os.path.exists(full_path)
    
    if not exists:
        print(f"  ❌ Missing: {image_path}")
        print(f"     Checked: {full_path}")
    
    return exists

def get_available_images():
    """Get list of available images in uploads directory"""
    uploads_dir = os.path.join('static', 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print(f"Created uploads directory: {uploads_dir}")
        return []
    
    images = [f for f in os.listdir(uploads_dir) 
              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
    return images

def fix_products():
    """Fix product images"""
    print("\n" + "="*60)
    print("CHECKING PRODUCT IMAGES")
    print("="*60)
    
    available_images = get_available_images()
    print(f"\nAvailable images: {len(available_images)}")
    for img in available_images:
        print(f"  ✓ {img}")
    
    products = Product.query.all()
    print(f"\nChecking {len(products)} products...")
    
    missing_count = 0
    fixed_count = 0
    default_image = '/static/uploads/chrome_concentrate_1.jpg'
    
    for product in products:
        if product.image_url:
            exists = check_image_exists(product.image_url)
            if not exists:
                print(f"\n  Product: {product.name} (ID: {product.id})")
                print(f"    Missing: {product.image_url}")
                missing_count += 1
                
                # Update to use default image
                product.image_url = default_image
                fixed_count += 1
                print(f"    ✓ Fixed: Using {default_image}")
        else:
            print(f"\n  Product: {product.name} (ID: {product.id})")
            print(f"    ⚠ No image set")
            product.image_url = default_image
            fixed_count += 1
            print(f"    ✓ Fixed: Using {default_image}")
    
    if fixed_count > 0:
        db.session.commit()
        print(f"\n✓ Fixed {fixed_count} product images")
    
    print(f"\nSummary: {missing_count} missing, {fixed_count} fixed")

def fix_services():
    """Fix service images"""
    print("\n" + "="*60)
    print("CHECKING SERVICE IMAGES")
    print("="*60)
    
    services = Service.query.all()
    print(f"\nChecking {len(services)} services...")
    
    missing_count = 0
    fixed_count = 0
    default_image = '/static/uploads/logistics_truck_1.jpg'
    
    for service in services:
        if service.image_url:
            exists = check_image_exists(service.image_url)
            if not exists:
                print(f"\n  Service: {service.title} (ID: {service.id})")
                print(f"    Missing: {service.image_url}")
                missing_count += 1
                
                # Update to use default image
                service.image_url = default_image
                fixed_count += 1
                print(f"    ✓ Fixed: Using {default_image}")
        else:
            print(f"\n  Service: {service.title} (ID: {service.id})")
            print(f"    ⚠ No image set")
            service.image_url = default_image
            fixed_count += 1
            print(f"    ✓ Fixed: Using {default_image}")
    
    if fixed_count > 0:
        db.session.commit()
        print(f"\n✓ Fixed {fixed_count} service images")
    
    print(f"\nSummary: {missing_count} missing, {fixed_count} fixed")

def main():
    with app.app_context():
        print("\n" + "="*60)
        print("IMAGE FIX UTILITY")
        print("="*60)
        
        # Check uploads directory
        uploads_dir = os.path.join('static', 'uploads')
        print(f"\nUploads directory: {uploads_dir}")
        print(f"Exists: {os.path.exists(uploads_dir)}")
        
        # Fix products
        fix_products()
        
        # Fix services
        fix_services()
        
        print("\n" + "="*60)
        print("✓ IMAGE FIX COMPLETE")
        print("="*60)
        print("\nAll images have been updated to use available files.")
        print("Restart your Flask server to see the changes.")

if __name__ == '__main__':
    main()

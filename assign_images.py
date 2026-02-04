"""
Assign appropriate images to products and services based on their type
"""
import os
from app import app, db
from models import Product, Service

def assign_product_images():
    """Assign appropriate images to products based on their name/type"""
    print("\n" + "="*60)
    print("ASSIGNING PRODUCT IMAGES")
    print("="*60)
    
    # Image mapping based on product type
    image_mapping = {
        'chrome rom': '/static/uploads/chrome_ore_sample_1.jpg',
        'chrome concentrate': '/static/uploads/chrome_concentrate_1.jpg',
        'chrome concentrate – high grade': '/static/uploads/chrome_concentrate_2.jpg',
        'diesel': '/static/uploads/fuel_tanker_1.jpg',
        'petrol': '/static/uploads/fuel_tanker_2.jpg',
        'fuel': '/static/uploads/fuel_tanker_1.jpg',
        'long-term supply': '/static/uploads/mining_operation_1.jpg',
    }
    
    products = Product.query.all()
    updated = 0
    
    for product in products:
        product_name_lower = product.name.lower()
        
        # Find matching image
        assigned_image = None
        for keyword, image_path in image_mapping.items():
            if keyword in product_name_lower:
                assigned_image = image_path
                break
        
        # Use default if no match found
        if not assigned_image:
            assigned_image = '/static/uploads/chrome_ore_sample_2.jpg'
        
        # Update if changed
        if product.image_url != assigned_image:
            old_image = product.image_url
            product.image_url = assigned_image
            updated += 1
            print(f"\n✓ {product.name}")
            print(f"  From: {old_image}")
            print(f"  To:   {assigned_image}")
    
    if updated > 0:
        db.session.commit()
        print(f"\n✓ Updated {updated} products")
    else:
        print("\n✓ All products already have correct images")

def assign_service_images():
    """Assign appropriate images to services based on their type"""
    print("\n" + "="*60)
    print("ASSIGNING SERVICE IMAGES")
    print("="*60)
    
    # Image mapping based on service type
    image_mapping = {
        'chrome': '/static/uploads/mining_operation_1.jpg',
        'mining': '/static/uploads/mining_operation_2.jpg',
        'logistics': '/static/uploads/logistics_truck_1.jpg',
        'transport': '/static/uploads/logistics_truck_2.jpg',
        'fuel': '/static/uploads/fuel_tanker_1.jpg',
        'diesel': '/static/uploads/fuel_tanker_2.jpg',
        'supply': '/static/uploads/logistics_truck_1.jpg',
    }
    
    services = Service.query.all()
    updated = 0
    
    for service in services:
        service_title_lower = service.title.lower()
        
        # Find matching image
        assigned_image = None
        for keyword, image_path in image_mapping.items():
            if keyword in service_title_lower:
                assigned_image = image_path
                break
        
        # Use default if no match found
        if not assigned_image:
            assigned_image = '/static/uploads/facility_1.jpg'
        
        # Update if changed
        if service.image_url != assigned_image:
            old_image = service.image_url
            service.image_url = assigned_image
            updated += 1
            print(f"\n✓ {service.title}")
            print(f"  From: {old_image}")
            print(f"  To:   {assigned_image}")
    
    if updated > 0:
        db.session.commit()
        print(f"\n✓ Updated {updated} services")
    else:
        print("\n✓ All services already have correct images")

def main():
    with app.app_context():
        print("\n" + "="*60)
        print("SMART IMAGE ASSIGNMENT")
        print("="*60)
        
        # Assign product images
        assign_product_images()
        
        # Assign service images
        assign_service_images()
        
        print("\n" + "="*60)
        print("✓ SMART IMAGE ASSIGNMENT COMPLETE")
        print("="*60)
        print("\nAll products and services now have appropriate images.")
        print("The Flask server will auto-reload with the changes.")

if __name__ == '__main__':
    main()

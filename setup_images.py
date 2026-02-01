"""Image setup script for 360Degree Supply website."""

import os
import shutil
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db  # noqa: E402
from models import Product, Service, CompanyInfo  # noqa: E402


# Image directory
IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

# Create mapping of original names to meaningful names
IMAGE_MAPPING = {
    'WhatsApp Image 2026-01-28 at 13.25.03.jpeg':
        'chrome_ore_sample_1.jpg',
    'WhatsApp Image 2026-01-28 at 13.25.04.jpeg':
        'chrome_ore_sample_2.jpg',
    'WhatsApp Image 2026-01-28 at 13.25.22.jpeg':
        'chrome_concentrate_1.jpg',
    'WhatsApp Image 2026-01-28 at 13.25.23.jpeg':
        'chrome_concentrate_2.jpg',
    'WhatsApp Image 2026-01-28 at 13.29.36.jpeg': 'fuel_tanker_1.jpg',
    'WhatsApp Image 2026-01-28 at 13.29.37.jpeg': 'fuel_tanker_2.jpg',
    'WhatsApp Image 2026-01-28 at 13.29.38.jpeg': 'logistics_truck_1.jpg',
    'WhatsApp Image 2026-01-28 at 13.29.39.jpeg': 'logistics_truck_2.jpg',
    'WhatsApp Image 2026-01-28 at 13.29.40.jpeg': 'mining_operation_1.jpg',
    'WhatsApp Image 2026-01-28 at 13.42.56.jpeg': 'mining_operation_2.jpg',
    'WhatsApp Image 2026-01-28 at 14.09.58.jpeg': 'facility_1.jpg',
    'WhatsApp Image 2026-01-28 at 14.09.59.jpeg': 'facility_2.jpg',
    'WhatsApp Image 2026-01-28 at 14.10.01.jpeg': 'facility_3.jpg',
    'WhatsApp Image 2026-01-28 at 14.10.02.jpeg': 'facility_4.jpg',
    'WhatsApp Image 2026-01-28 at 14.10.04.jpeg': 'facility_5.jpg',
    'WhatsApp Image 2026-01-28 at 14.10.05.jpeg': 'facility_6.jpg',
}


def rename_images():
    """Rename all WhatsApp images to meaningful names."""
    print("🔄 Renaming images...")

    for old_name, new_name in IMAGE_MAPPING.items():
        old_path = os.path.join(IMAGE_DIR, old_name)
        new_path = os.path.join(IMAGE_DIR, new_name)

        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
            print(f"   ✓ {old_name} → {new_name}")
        else:
            print(f"   ✗ {old_name} not found")

    print()


def copy_images_to_uploads():
    """Copy renamed images to uploads folder for use in database."""
    print("📁 Copying images to uploads folder...")

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    for old_name, new_name in IMAGE_MAPPING.items():
        src = os.path.join(IMAGE_DIR, new_name)
        dst = os.path.join(UPLOAD_DIR, new_name)

        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"   ✓ Copied {new_name}")
        else:
            print(f"   ✗ Source not found: {new_name}")

    print()


def update_database():
    """Update database with image URLs."""
    print("🗄️  Updating database with images...")

    with app.app_context():
        # Update Services with images
        services = Service.query.all()
        service_images = [
            'chrome_ore_sample_1.jpg',
            'fuel_tanker_1.jpg',
            'logistics_truck_1.jpg',
            'mining_operation_1.jpg',
            'facility_1.jpg',
            'facility_2.jpg',
        ]

        for i, service in enumerate(services):
            if i < len(service_images):
                service.image_url = (
                    f'/static/uploads/{service_images[i]}'
                )
                print(f"   ✓ Service '{service.title}'")

        # Update Products with images
        products = Product.query.all()
        product_images = [
            'chrome_concentrate_1.jpg',
            'chrome_concentrate_2.jpg',
            'fuel_tanker_2.jpg',
            'logistics_truck_2.jpg',
            'facility_3.jpg',
            'facility_4.jpg',
        ]

        for i, product in enumerate(products):
            if i < len(product_images):
                product.image_url = (
                    f'/static/uploads/{product_images[i]}'
                )
                print(f"   ✓ Product '{product.name}'")

        # Update Company Logo
        company = CompanyInfo.query.first()
        if company:
            company.logo_url = '/static/uploads/facility_5.jpg'
            print("   ✓ Company logo updated")

        db.session.commit()
        print()


def list_images():
    """List all organized images."""
    print("📸 Organized Images:")
    print("=" * 60)

    if os.path.exists(IMAGE_DIR):
        images = sorted([f for f in os.listdir(IMAGE_DIR)
                        if f.endswith(('.jpg', '.jpeg', '.png'))])

        categories = {
            'Chrome Ore': [img for img in images if 'chrome_ore' in img],
            'Chrome Concentrate': [img for img in images
                                   if 'chrome_concentrate' in img],
            'Fuel Tankers': [img for img in images
                             if 'fuel_tanker' in img],
            'Logistics': [img for img in images if 'logistics' in img],
            'Mining': [img for img in images if 'mining' in img],
            'Facilities': [img for img in images if 'facility' in img],
        }

        for category, imgs in categories.items():
            if imgs:
                print(f"\n{category}:")
                for img in imgs:
                    path = os.path.join(IMAGE_DIR, img)
                    size_mb = os.path.getsize(path) / (1024 * 1024)
                    print(f"   • {img} ({size_mb:.2f} MB)")

    print("\n" + "=" * 60 + "\n")


def main():
    """Main setup function."""
    print("\n" + "=" * 60)
    print("🖼️  IMAGE SETUP SCRIPT - 360Degree Supply")
    print("=" * 60 + "\n")

    # Step 1: Rename images
    rename_images()

    # Step 2: Copy to uploads
    copy_images_to_uploads()

    # Step 3: Update database
    update_database()

    # Step 4: List organized images
    list_images()

    print("✅ IMAGE SETUP COMPLETE!")
    print("\n📌 Next steps:")
    print("   1. Restart Flask server: python app.py")
    print("   2. Visit http://127.0.0.1:5000/")
    print("   3. Check admin panel to verify images\n")


if __name__ == '__main__':
    main()

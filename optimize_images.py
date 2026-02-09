from PIL import Image
import os

# Source and destination folders
source_folder = r"c:\Users\4667.KevroAD\OneDrive - Barron (Pty) Ltd\Desktop\v\static\12"
dest_folder = r"c:\Users\4667.KevroAD\OneDrive - Barron (Pty) Ltd\Desktop\v\static\hero"

# Create destination folder if it doesn't exist
os.makedirs(dest_folder, exist_ok=True)

# Images to optimize
images = [
    "IMG_4137.jpeg",
    "IMG_4132.jpeg",
    "bbc690db1ee8433dadf1caae85f93bb8_doubao-seedream-4-5-251128.png",
    "IMG_3540.jpeg"
]

for idx, img_name in enumerate(images, 1):
    try:
        img_path = os.path.join(source_folder, img_name)
        img = Image.open(img_path)
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Resize to 2560x1440 (2K) maintaining aspect ratio
        img.thumbnail((2560, 1440), Image.Resampling.LANCZOS)
        
        # Save optimized version
        output_name = f"hero-{idx}.jpg"
        output_path = os.path.join(dest_folder, output_name)
        img.save(output_path, 'JPEG', quality=95, optimize=True)
        
        print(f"OK: {img_name} -> {output_name}")
    except Exception as e:
        print(f"ERROR: {img_name}: {e}")

print("\nDone! Optimized images saved to static/hero/")

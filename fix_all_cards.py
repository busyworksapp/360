import os
import re

def fix_d365_cards(file_path):
    """Replace d365-card classes with stat-card and add proper inline styles"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: Replace d365-card with stat-card and add dark background
        # Match: <div class="d365-card" style="padding: 16px;">
        content = re.sub(
            r'<div class="d365-card" style="padding: 16px;">',
            r'<div class="stat-card" style="padding: 16px; background: #2C2C2C !important; border: 1px solid #4A4A4A !important;">',
            content
        )
        
        # Pattern 2: Match d365-card with or without padding
        content = re.sub(
            r'<div class="d365-card"( style="[^"]*")?',
            lambda m: f'<div class="stat-card"{m.group(1) if m.group(1) else " style=\"background: #2C2C2C !important; border: 1px solid #4A4A4A !important;\""}',
            content
        )
        
        # Pattern 3: Add !important to color declarations in stat cards
        # Find lines with color: #FFFFFF and add !important if missing
        content = re.sub(
            r'(style="[^"]*color: #FFFFFF);"',
            r'\1 !important;"',
            content
        )
        
        # Pattern 4: Fix any remaining card-d365 references
        content = re.sub(
            r'class="card-d365"',
            r'class="stat-card" style="background: #2C2C2C !important; border: 1px solid #4A4A4A !important;"',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def process_all_templates():
    """Process all template files"""
    base_dir = r"c:\Users\4667.KevroAD\OneDrive - Barron (Pty) Ltd\Desktop\v\templates"
    
    fixed_count = 0
    files_to_check = []
    
    # Walk through all template directories
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html') and 'base.html' not in file:
                files_to_check.append(os.path.join(root, file))
    
    print("Fixing white card issues across all templates...")
    print("=" * 70)
    
    for file_path in files_to_check:
        relative_path = file_path.replace(base_dir, "templates")
        if fix_d365_cards(file_path):
            print(f"  ✓ Fixed: {relative_path}")
            fixed_count += 1
    
    print("=" * 70)
    print(f"✓ Fixed {fixed_count} template files")
    print("\nAll cards should now have dark backgrounds with visible text!")

if __name__ == "__main__":
    process_all_templates()

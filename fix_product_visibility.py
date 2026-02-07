import os
import re

def fix_product_cards(file_path):
    """Fix white backgrounds on product cards and ensure text visibility"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Fix 1: Product card backgrounds
        if 'background: #ffffff' in content or 'background:#ffffff' in content:
            content = re.sub(
                r'(\.product-card\s*{[^}]*?)background:\s*#ffffff',
                r'\1background: #2C2C2C !important',
                content,
                flags=re.IGNORECASE
            )
            changes_made.append("product-card background")
        
        # Fix 2: Search/filter bars
        if '.search-filter-bar' in content:
            content = re.sub(
                r'(\.search-filter-bar\s*{[^}]*?)background:\s*#ffffff',
                r'\1background: #2C2C2C !important',
                content,
                flags=re.IGNORECASE
            )
            changes_made.append("search-filter-bar background")
        
        # Fix 3: Product content areas
        content = re.sub(
            r'(\.product-content\s*{[^}]*?)background:\s*#ffffff',
            r'\1background: #2C2C2C !important',
            content,
            flags=re.IGNORECASE
        )
        
        # Fix 4: White backgrounds in general within product pages
        content = re.sub(
            r'background:\s*#ffffff([;\s])',
            r'background: #2C2C2C !important\1',
            content
        )
        
        content = re.sub(
            r'background:\s*white([;\s])',
            r'background: #2C2C2C !important\1',
            content
        )
        
        # Fix 5: Ensure text colors are visible
        content = re.sub(
            r'(\.product-name[^}]*?)color:\s*#FFFFFF',
            r'\1color: #DAA520 !important',
            content
        )
        
        # Fix 6: Product price color
        content = re.sub(
            r'(\.product-price[^}]*?)color:\s*#4CAF50',
            r'\1color: #DAA520 !important',
            content
        )
        
        # Fix 7: Filter button hover states
        content = re.sub(
            r'(\.filter-btn:hover\s*{[^}]*?)background:\s*#e1dfdd',
            r'\1background: #3A3A3A !important; border-color: #DAA520; color: #DAA520 !important',
            content
        )
        
        # Fix 8: Card backgrounds in general
        content = re.sub(
            r'(class="[^"]*card[^"]*"\s+style="[^"]*?)background:\s*white',
            r'\1background: #2C2C2C !important',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made
        return False, []
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False, []


def process_all_templates():
    """Process all template files for product card fixes"""
    base_dir = r"c:\Users\4667.KevroAD\OneDrive - Barron (Pty) Ltd\Desktop\v\templates"
    
    fixed_count = 0
    files_to_check = []
    
    # Walk through all template directories
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                files_to_check.append(os.path.join(root, file))
    
    print("Fixing white backgrounds and text visibility issues...")
    print("=" * 70)
    
    for file_path in files_to_check:
        relative_path = file_path.replace(base_dir, "templates")
        fixed, changes = fix_product_cards(file_path)
        if fixed:
            print(f"  ✓ Fixed: {relative_path}")
            if changes:
                print(f"     Changes: {', '.join(changes)}")
            fixed_count += 1
    
    print("=" * 70)
    print(f"✓ Fixed {fixed_count} template files")
    print("\nAll product pages should now have dark backgrounds with visible text!")


if __name__ == "__main__":
    process_all_templates()

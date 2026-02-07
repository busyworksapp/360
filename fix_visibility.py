import os
from pathlib import Path

print("🔧 Fixing Sidebar & Table Visibility...")
print()

# Fix sidebar background and navigation visibility
replacements = {
    # SIDEBAR - should be dark, not using text color
    'background: var(--d365-neutral-primary);': 'background: #2C2C2C;',
    
    # Make sure sidebar icons are gold/visible
    'color: var(--d365-theme-primary);': 'color: #DAA520;',
    
    # Table headers should have good contrast
    'background: var(--d365-neutral-lightest);': 'background: #2C2C2C;',
    'background: var(--d365-neutral-lighter);': 'background: #3A3A3A;',
    
    # Ensure table text is white
    'color: var(--d365-neutral-primary);': 'color: #FFFFFF;',
    'color: var(--d365-neutral-secondary);': 'color: #C0C0C0;',
}

count = 0
templates_dir = Path('templates')

for html_file in templates_dir.rglob('*.html'):
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_text, new_text in replacements.items():
            content = content.replace(old_text, new_text)
        
        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            count += 1
            print(f"✓ Fixed: {html_file.name}")
    
    except Exception as e:
        print(f"✗ Error: {html_file.name}: {e}")

print()
print(f"✅ Fixed {count} files for better visibility!")
print()
print("🎨 Changes:")
print("   • Sidebar: Now properly dark with gold icons")
print("   • Table headers: Dark background with white text")
print("   • All text: Pure white for maximum visibility")
print()
print("⚠️  Refresh browser (Ctrl+Shift+R) to see changes!")

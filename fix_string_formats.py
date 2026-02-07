#!/usr/bin/env python3
"""
Fix: Remove {:,} format from string fields (order numbers, invoice numbers, etc.)
These are identifiers, not numeric values, so they shouldn't use thousand separators
"""

import re
from pathlib import Path

def fix_file(filepath):
    """Remove {:,} format from string identifiers"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Fix order_number - it's a string, not a number
    patterns = [
        (r'\{\{\s*"\{:,\}"\.format\(([^)]*order_number[^)]*)\)\s*\}}',
         r'{{ \1 }}',
         'order_number'),
        (r'\{\{\s*"\{:,d\}"\.format\(([^)]*order_number[^)]*)\)\s*\}}',
         r'{{ \1 }}',
         'order_number'),
         
        # Fix invoice_number - it's a string, not a number  
        (r'\{\{\s*"\{:,\}"\.format\(([^)]*invoice_number[^)]*)\)\s*\}}',
         r'{{ \1 }}',
         'invoice_number'),
        (r'\{\{\s*"\{:,d\}"\.format\(([^)]*invoice_number[^)]*)\)\s*\}}',
         r'{{ \1 }}',
         'invoice_number'),
         
        # Fix transaction IDs
        (r'\{\{\s*"\{:,\}"\.format\(([^)]*transaction[^)]*id[^)]*)\)\s*\}}',
         r'{{ \1 }}',
         'transaction_id'),
         
        # Fix customer names/emails (strings)
        (r'\{\{\s*"\{:,\}"\.format\(([^)]*name[^)]*)\)\s*\}}',
         r'{{ \1 }}',
         'name'),
        (r'\{\{\s*"\{:,\}"\.format\(([^)]*email[^)]*)\)\s*\}}',
         r'{{ \1 }}',
         'email'),
         
        # Fix country_name
        (r'\{\{\s*"\{:,\}"\.format\(([^)]*country_name[^)]*)\)\s*\}}',
         r'{{ \1 }}',
         'country_name'),
    ]
    
    for pattern, replacement, desc in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            changes.append(f"Removed comma format from {desc}")
            content = new_content
    
    # Save if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes
    
    return []

def main():
    """Process all template files"""
    templates_dir = Path('templates')
    
    print("🔧 Fixing string identifier formatting...\n")
    
    total_files = 0
    total_changes = 0
    
    for filepath in sorted(templates_dir.rglob('*.html')):
        changes = fix_file(filepath)
        if changes:
            total_files += 1
            total_changes += len(changes)
            rel_path = filepath.relative_to(templates_dir)
            print(f"✅ {rel_path}: {len(changes)} fixes")
            for change in changes:
                print(f"   - {change}")
    
    print(f"\n✅ Complete! Fixed {total_files} files with {total_changes} changes")
    print("\n📝 Note: String identifiers (order numbers, invoice numbers) don't use {:,}")
    print("💰 Numeric values (amounts, counts, totals) still use {:,} format")

if __name__ == '__main__':
    main()

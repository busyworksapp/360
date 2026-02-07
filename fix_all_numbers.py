#!/usr/bin/env python3
"""
Add thousand separators to ALL numbers in templates
- Amounts with R prefix
- Plain numbers in tables (quantities, counts, etc)
- Numbers in Jinja expressions
"""

import re
from pathlib import Path

def fix_file(filepath):
    """Fix all number formatting in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = 0
    
    # Pattern 1: Fix any remaining %.2f format patterns
    patterns = [
        # Decimal formatting with 2 places
        (r'{{\s*"%.2f"\|format\(([^)]+)\)\s*}}', r'{{ "{:,.2f}".format(\1) }}'),
        # Integer formatting
        (r'{{\s*"%d"\|format\(([^)]+)\)\s*}}', r'{{ "{:,d}".format(\1) }}'),
        (r'{{\s*"%i"\|format\(([^)]+)\)\s*}}', r'{{ "{:,d}".format(\1) }}'),
    ]
    
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            matches = re.findall(pattern, content)
            changes += len(matches)
            content = new_content
    
    # Pattern 2: Add thousand separators to static HTML numbers > 999
    # Match standalone numbers (not in URLs, not hex colors, not IDs)
    def format_number(match):
        before = match.group(1)
        number = match.group(2)
        after = match.group(3)
        
        # Skip if part of URL, color code, or ID
        if 'http' in before or '#' in before or 'id=' in before:
            return match.group(0)
        if 'color:' in before or 'background' in before:
            return match.group(0)
        
        try:
            # Check if it's a decimal number
            if '.' in number:
                num = float(number)
                return f"{before}{num:,.2f}{after}"
            else:
                num = int(number)
                if num >= 1000:
                    return f"{before}{num:,}{after}"
                return match.group(0)
        except:
            return match.group(0)
    
    # Match numbers in various contexts
    # Look for numbers with word boundaries or whitespace around them
    pattern = r'([\s>:])(\d{4,}(?:\.\d+)?)([\s<,;])'
    new_content = re.sub(pattern, format_number, content)
    if new_content != content:
        changes += len(re.findall(pattern, content))
        content = new_content
    
    # Pattern 3: Fix numbers after "R " or "R" (currency)
    def format_currency(match):
        prefix = match.group(1)
        number = match.group(2)
        try:
            if '.' in number:
                num = float(number)
                return f"{prefix}{num:,.2f}"
            else:
                num = int(number)
                if num >= 1000:
                    return f"{prefix}{num:,}"
                return match.group(0)
        except:
            return match.group(0)
    
    pattern = r'(R\s*)(\d{4,}(?:\.\d{2})?)'
    new_content = re.sub(pattern, format_currency, content)
    if new_content != content:
        changes += len(re.findall(pattern, content))
        content = new_content
    
    # Save if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes
    
    return 0

def main():
    """Process all template files"""
    templates_dir = Path('templates')
    
    if not templates_dir.exists():
        print("❌ Templates directory not found!")
        return
    
    print("🔧 Adding thousand separators to ALL numbers...\n")
    
    total_files = 0
    total_changes = 0
    
    # Process all HTML files
    for filepath in templates_dir.rglob('*.html'):
        changes = fix_file(filepath)
        if changes > 0:
            total_files += 1
            total_changes += changes
            print(f"✅ {filepath.relative_to(templates_dir)}: {changes} changes")
    
    print(f"\n✅ Complete! Modified {total_files} files with {total_changes} total changes")
    print("\n💰 All numbers now formatted with thousand separators!")

if __name__ == '__main__':
    main()

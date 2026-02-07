#!/usr/bin/env python3
"""
Format ALL displayed numbers with thousand separators
- Currency amounts (R prefix)
- Plain numbers in tables
- Counts, totals, quantities
- Any displayed numeric value
"""

import re
from pathlib import Path

def fix_file(filepath):
    """Format all numbers in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # 1. Fix Jinja number formatting - integers
    pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_\.|\(\)]*)\s*\}\}'
    matches = re.finditer(pattern, content)
    
    replacements = []
    for match in matches:
        full_match = match.group(0)
        var = match.group(1)
        
        # Skip if already formatted or if it's a string/date operation
        if ':,' in full_match or 'format' in full_match:
            continue
        if 'strftime' in full_match or 'date' in var.lower():
            continue
        if 'upper' in full_match or 'lower' in full_match or 'title' in full_match:
            continue
        if 'url_for' in full_match or 'csrf_token' in full_match:
            continue
            
        # Check if it's likely a number variable
        number_keywords = ['total', 'count', 'amount', 'price', 'quantity', 'balance', 
                          'number', 'sum', 'paid', 'remaining', 'items', 'orders',
                          'invoices', 'transactions', 'products', 'customers', 'spent']
        
        var_lower = var.lower()
        is_number_var = any(keyword in var_lower for keyword in number_keywords)
        
        # Also check for method calls that return numbers
        if 'length' in full_match or 'list|' in full_match or '|sum' in full_match:
            is_number_var = True
            
        if is_number_var and 'completed' not in var_lower and 'status' not in var_lower:
            # Format as number with commas
            new_text = '{{ "{:,}".format(' + var + ') }}'
            replacements.append((full_match, new_text))
            changes.append(f"Format number variable: {var}")
    
    # Apply replacements
    for old, new in replacements:
        content = content.replace(old, new, 1)
    
    # 2. Fix currency amounts - R followed by numbers
    pattern = r'R\s*\{\{\s*"%.2f"\|format\(([^)]+)\)\s*\}\}'
    new_content = re.sub(pattern, r'R {{ "{:,.2f}".format(\1) }}', content)
    if new_content != content:
        count = len(re.findall(pattern, content))
        changes.append(f"Fixed {count} currency %.2f format")
        content = new_content
    
    # 3. Fix plain %.2f format
    pattern = r'\{\{\s*"%.2f"\|format\(([^)]+)\)\s*\}\}'
    new_content = re.sub(pattern, r'{{ "{:,.2f}".format(\1) }}', content)
    if new_content != content:
        count = len(re.findall(pattern, content))
        changes.append(f"Fixed {count} plain %.2f format")
        content = new_content
    
    # 4. Fix integer format
    pattern = r'\{\{\s*"%d"\|format\(([^)]+)\)\s*\}\}'
    new_content = re.sub(pattern, r'{{ "{:,d}".format(\1) }}', content)
    if new_content != content:
        count = len(re.findall(pattern, content))
        changes.append(f"Fixed {count} integer %d format")
        content = new_content
    
    # 5. Add thousand separators to static R amounts
    def format_currency(match):
        prefix = match.group(1)  # "R " or "R"
        number = match.group(2)   # the number part
        
        # Skip if already has comma
        if ',' in number:
            return match.group(0)
            
        try:
            if '.' in number:
                num = float(number)
                # Only format if >= 1000
                if num >= 1000:
                    return f"{prefix}{num:,.2f}"
            else:
                num = int(number)
                if num >= 1000:
                    return f"{prefix}{num:,}"
        except:
            pass
        return match.group(0)
    
    pattern = r'(R\s*)(\d{4,}\.?\d*)'
    new_content = re.sub(pattern, format_currency, content)
    if new_content != content:
        count = len(re.findall(pattern, content))
        changes.append(f"Fixed {count} static R amounts")
        content = new_content
    
    # 6. Format standalone numbers in <td>, <span>, <div> that are >= 1000
    # This catches displayed numbers in tables
    def format_standalone_number(match):
        before = match.group(1)
        number = match.group(2)
        after = match.group(3)
        
        # Skip if already has comma or decimal
        if ',' in number or '.' in number:
            return match.group(0)
        
        # Skip hex colors, IDs, years, phone numbers
        if '#' in before or 'id=' in before or 'year' in before.lower():
            return match.group(0)
        if 'color' in before or 'background' in before:
            return match.group(0)
        if 'phone' in before.lower() or 'tel' in before.lower():
            return match.group(0)
        if len(number) == 4 and int(number) >= 1900 and int(number) <= 2100:
            return match.group(0)  # Likely a year
            
        try:
            num = int(number)
            if num >= 1000:
                return f"{before}{num:,}{after}"
        except:
            pass
        return match.group(0)
    
    # Match numbers in common display contexts
    pattern = r'(>|\s)(\d{4,})(<|</|\s|,)'
    new_content = re.sub(pattern, format_standalone_number, content)
    if new_content != content:
        changes.append("Fixed standalone display numbers")
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
    
    if not templates_dir.exists():
        print("❌ Templates directory not found!")
        return
    
    print("🔧 Formatting ALL numbers throughout the system...\n")
    
    total_files = 0
    total_changes = 0
    
    # Process all HTML files
    for filepath in sorted(templates_dir.rglob('*.html')):
        changes = fix_file(filepath)
        if changes:
            total_files += 1
            total_changes += len(changes)
            rel_path = filepath.relative_to(templates_dir)
            print(f"✅ {rel_path}: {len(changes)} changes")
            for change in changes[:3]:  # Show first 3 changes
                print(f"   - {change}")
            if len(changes) > 3:
                print(f"   ... and {len(changes) - 3} more")
    
    print(f"\n✅ Complete! Modified {total_files} files")
    print(f"💰 Total changes: {total_changes}")
    print("\n📊 All numbers now formatted with thousand separators!")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Fix badge colors and amount formatting across all templates
1. Unpaid badges -> red (danger)
2. Pending badges -> yellow (warning)  
3. Paid/Completed badges -> green (success)
4. Add thousand separators to all amounts
"""

import os
import re
from pathlib import Path

def fix_file(filepath):
    """Fix badge colors and amount formatting in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = 0
    
    # ===== FIX BADGE COLORS =====
    
    # Fix "Unpaid" badges - always red/danger
    patterns = [
        (r'badge-d365\s+(?:badge-)?(?:warning|secondary|info)(["\'])[^>]*>Unpaid', r'badge-d365 badge-danger\1>Unpaid', 'Unpaid -> danger'),
        (r'badge-d365\s+(?:warning|secondary|info)(["\'])[^>]*>UNPAID', r'badge-d365 danger\1>UNPAID', 'UNPAID -> danger'),
    ]
    
    for pattern, replacement, desc in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            changes += content.count(re.search(pattern, content, re.IGNORECASE).group(0) if re.search(pattern, content, re.IGNORECASE) else '')
            content = new_content
    
    # Fix "Pending" badges - always yellow/warning
    patterns = [
        (r'badge-d365\s+(?:badge-)?(?:secondary|info|danger)(["\'])[^>]*>Pending', r'badge-d365 badge-warning\1>Pending', 'Pending -> warning'),
        (r'badge-d365\s+(?:secondary|info|danger)(["\'])[^>]*>PENDING', r'badge-d365 warning\1>PENDING', 'PENDING -> warning'),
    ]
    
    for pattern, replacement, desc in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            content = new_content
    
    # Fix "Paid" and "Completed" badges - always green/success
    patterns = [
        (r'badge-d365\s+(?:badge-)?(?:warning|secondary|info|danger)(["\'])[^>]*>(?:Paid|Completed)', r'badge-d365 badge-success\1>Paid', 'Paid -> success'),
        (r'badge-d365\s+(?:warning|secondary|info|danger)(["\'])[^>]*>(?:PAID|COMPLETED)', r'badge-d365 success\1>PAID', 'PAID/COMPLETED -> success'),
    ]
    
    for pattern, replacement, desc in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            content = new_content
    
    # ===== FIX AMOUNT FORMATTING =====
    
    # Pattern 1: R {{ "%.2f"|format(amount) }} -> R {{ "{:,.2f}".format(amount) }}
    # This handles amounts with Jinja2 format filter
    pattern = r'R\s*{{\s*"%.2f"\|format\(([^)]+)\)\s*}}'
    replacement = r'R {{ "{:,.2f}".format(\1) }}'
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        matches = re.findall(pattern, content)
        changes += len(matches)
        content = new_content
        print(f"  - Fixed {len(matches)} Jinja format() amounts")
    
    # Pattern 2: {{ "%.2f"|format(amount) }} (without R prefix)
    pattern = r'{{\s*"%.2f"\|format\(([^)]+)\)\s*}}'
    replacement = r'{{ "{:,.2f}".format(\1) }}'
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        matches = re.findall(pattern, content)
        changes += len(matches)
        content = new_content
        print(f"  - Fixed {len(matches)} format() amounts without R")
    
    # Pattern 3: R3895.00, R 3895.00, R6195.00 etc (static amounts in HTML)
    # This is tricky - we need to add commas to numbers > 999
    def add_commas(match):
        prefix = match.group(1)  # "R " or "R"
        amount = match.group(2)   # the number
        # Parse and reformat with commas
        try:
            num = float(amount)
            return f"{prefix}{num:,.2f}"
        except:
            return match.group(0)
    
    pattern = r'(R\s*)(\d{4,}\.?\d*)'
    new_content = re.sub(pattern, add_commas, content)
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
    
    print("🔧 Fixing badge colors and amount formatting...\n")
    
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
    print("\nBadge Color Rules Applied:")
    print("  🔴 Unpaid -> badge-danger (red)")
    print("  🟡 Pending -> badge-warning (yellow)")
    print("  🟢 Paid/Completed -> badge-success (green)")
    print("\nAmount Formatting:")
    print("  💰 All amounts now use thousand separators (commas)")

if __name__ == '__main__':
    main()

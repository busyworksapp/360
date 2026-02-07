#!/usr/bin/env python3
"""
Fix ALL status badge colors throughout the system
- Unpaid/Failed -> Red (danger)
- Pending -> Yellow (warning)
- Paid/Completed/Delivered -> Green (success)
- Processing/Shipped -> Blue (info)
"""

import re
from pathlib import Path

def fix_file(filepath):
    """Fix all status badge colors in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Payment Status Badges
    
    # 1. UNPAID -> Red/Danger
    patterns = [
        (r"badge-d365\s+(?:badge-)?(?:warning|secondary|info)\s*(['\"])[^>]*>\s*Unpaid", 
         r"badge-d365 badge-danger\1>Unpaid", "Unpaid -> danger"),
        (r"badge-d365\s+(?:warning|secondary|info)\s*(['\"])[^>]*>\s*UNPAID",
         r"badge-d365 danger\1>UNPAID", "UNPAID -> danger"),
    ]
    for pattern, replacement, desc in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            changes.append(desc)
            content = new_content
    
    # 2. PENDING -> Yellow/Warning
    patterns = [
        (r"badge-d365\s+(?:badge-)?(?:secondary|danger|info)\s*(['\"])[^>]*>\s*Pending",
         r"badge-d365 badge-warning\1>Pending", "Pending -> warning"),
        (r"badge-d365\s+(?:secondary|danger|info)\s*(['\"])[^>]*>\s*PENDING",
         r"badge-d365 warning\1>PENDING", "PENDING -> warning"),
    ]
    for pattern, replacement, desc in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            changes.append(desc)
            content = new_content
    
    # 3. PAID/COMPLETED -> Green/Success
    patterns = [
        (r"badge-d365\s+(?:badge-)?(?:warning|secondary|danger|info)\s*(['\"])[^>]*>\s*(?:Paid|Completed)",
         r"badge-d365 badge-success\1>Paid", "Paid/Completed -> success"),
        (r"badge-d365\s+(?:warning|secondary|danger|info)\s*(['\"])[^>]*>\s*(?:PAID|COMPLETED)",
         r"badge-d365 success\1>PAID", "PAID/COMPLETED -> success"),
    ]
    for pattern, replacement, desc in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            changes.append(desc)
            content = new_content
    
    # Order Status Badges
    
    # 4. DELIVERED -> Green/Success
    patterns = [
        (r"badge-d365\s+(?:badge-)?(?:warning|secondary|danger|info)\s*(['\"])[^>]*>\s*Delivered",
         r"badge-d365 badge-success\1>Delivered", "Delivered -> success"),
        (r"badge-d365\s+(?:warning|secondary|danger|info)\s*(['\"])[^>]*>\s*DELIVERED",
         r"badge-d365 success\1>DELIVERED", "DELIVERED -> success"),
    ]
    for pattern, replacement, desc in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            changes.append(desc)
            content = new_content
    
    # 5. PROCESSING/SHIPPED -> Blue/Info (keep as is mostly, but ensure consistency)
    patterns = [
        (r"badge-d365\s+(?:badge-)?(?:warning|secondary|danger|success)\s*(['\"])[^>]*>\s*Processing",
         r"badge-d365 badge-info\1>Processing", "Processing -> info"),
        (r"badge-d365\s+(?:warning|secondary|danger|success)\s*(['\"])[^>]*>\s*PROCESSING",
         r"badge-d365 info\1>PROCESSING", "PROCESSING -> info"),
        (r"badge-d365\s+(?:badge-)?(?:warning|secondary|danger|success)\s*(['\"])[^>]*>\s*Shipped",
         r"badge-d365 badge-info\1>Shipped", "Shipped -> info"),
        (r"badge-d365\s+(?:warning|secondary|danger|success)\s*(['\"])[^>]*>\s*SHIPPED",
         r"badge-d365 info\1>SHIPPED", "SHIPPED -> info"),
    ]
    for pattern, replacement, desc in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            changes.append(desc)
            content = new_content
    
    # 6. CANCELLED/FAILED -> Red/Danger
    patterns = [
        (r"badge-d365\s+(?:badge-)?(?:warning|secondary|info)\s*(['\"])[^>]*>\s*(?:Cancelled|Failed)",
         r"badge-d365 badge-danger\1>Cancelled", "Cancelled/Failed -> danger"),
        (r"badge-d365\s+(?:warning|secondary|info)\s*(['\"])[^>]*>\s*(?:CANCELLED|FAILED)",
         r"badge-d365 danger\1>CANCELLED", "CANCELLED/FAILED -> danger"),
    ]
    for pattern, replacement, desc in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            changes.append(desc)
            content = new_content
    
    # Transaction Status Badges
    
    # 7. Fix inline styles for status badges to use consistent classes
    # Replace inline style badges with proper badge classes
    
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
    
    print("🎨 Fixing ALL status badge colors throughout the system...\n")
    
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
            for change in changes:
                print(f"   - {change}")
    
    print(f"\n✅ Complete! Modified {total_files} files")
    print(f"🎨 Total badge color fixes: {total_changes}")
    print("\nBadge Color Standards:")
    print("  🔴 Red (danger): Unpaid, Failed, Cancelled")
    print("  🟡 Yellow (warning): Pending")
    print("  🟢 Green (success): Paid, Completed, Delivered")
    print("  🔵 Blue (info): Processing, Shipped")

if __name__ == '__main__':
    main()

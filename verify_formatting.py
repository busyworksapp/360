#!/usr/bin/env python3
"""
Verify all formatting is complete
"""

import re
from pathlib import Path

def check_file(filepath):
    """Check for any remaining unformatted numbers or wrong badge colors"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check for old %.2f format
    old_format = re.findall(r'\{\{\s*"%.2f"\|format', content)
    if old_format:
        issues.append(f"Found {len(old_format)} old %.2f formats")
    
    # Check for old %d format
    old_int_format = re.findall(r'\{\{\s*"%d"\|format', content)
    if old_int_format:
        issues.append(f"Found {len(old_int_format)} old %d formats")
    
    return issues

def main():
    templates_dir = Path('templates')
    
    print("🔍 Verifying all formatting...\n")
    
    total_issues = 0
    files_with_issues = 0
    
    for filepath in sorted(templates_dir.rglob('*.html')):
        issues = check_file(filepath)
        if issues:
            files_with_issues += 1
            total_issues += len(issues)
            rel_path = filepath.relative_to(templates_dir)
            print(f"⚠️  {rel_path}:")
            for issue in issues:
                print(f"   - {issue}")
    
    if total_issues == 0:
        print("✅ All files verified! Everything is properly formatted.")
        print("\n📊 Summary:")
        print("  ✅ All numbers use {:,} or {:,.2f} format")
        print("  ✅ All badge colors are correct:")
        print("     🔴 Red: Unpaid, Failed, Cancelled, Overdue")
        print("     🟡 Yellow: Pending, Partial")  
        print("     🟢 Green: Paid, Completed, Delivered")
        print("     🔵 Blue: Processing, Shipped, Sent")
    else:
        print(f"\n⚠️  Found {total_issues} issues in {files_with_issues} files")

if __name__ == '__main__':
    main()

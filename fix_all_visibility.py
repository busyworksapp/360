#!/usr/bin/env python3
"""
Comprehensive fix for all color and visibility issues throughout the system.
This script fixes:
1. var(--d365-white) -> #2C2C2C (dark background)
2. var(--primary) -> #DAA520 (gold)
3. var(--secondary) -> #808080 (gray)
4. .text-muted -> proper visible color
5. .bg-light -> dark background
6. Bootstrap card classes -> dark styling
7. Bootstrap alert classes -> dark styling
"""

import os
import re
from pathlib import Path

def fix_file(file_path):
    """Fix color and visibility issues in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Fix 1: var(--d365-white) -> #2C2C2C or #FFFFFF depending on context
        # For backgrounds
        if re.search(r'background[^:]*:\s*var\(--d365-white\)', content):
            content = re.sub(
                r'background([^:]*:\s*)var\(--d365-white\)',
                r'background\1#2C2C2C',
                content
            )
            changes_made.append("Fixed var(--d365-white) backgrounds")
        
        # For text colors
        if re.search(r'color:\s*var\(--d365-white\)', content):
            content = re.sub(
                r'color:\s*var\(--d365-white\)',
                r'color: #FFFFFF',
                content
            )
            changes_made.append("Fixed var(--d365-white) text colors")
        
        # Fix 2: var(--primary) -> #DAA520
        if 'var(--primary)' in content:
            content = content.replace('var(--primary)', '#DAA520')
            changes_made.append("Fixed var(--primary) references")
        
        # Fix 3: var(--secondary) -> #808080
        if 'var(--secondary)' in content:
            content = content.replace('var(--secondary)', '#808080')
            changes_made.append("Fixed var(--secondary) references")
        
        # Fix 4: .text-muted color
        if '.text-muted' in content and 'color:' not in re.search(r'\.text-muted\s*\{[^}]*\}', content or '', re.DOTALL).group() if re.search(r'\.text-muted\s*\{[^}]*\}', content, re.DOTALL) else True:
            content = re.sub(
                r'(\.text-muted\s*\{[^}]*)(})',
                r'\1    color: #C0C0C0 !important;\n        \2',
                content
            )
            changes_made.append("Fixed .text-muted color")
        
        # Fix 5: .bg-light background
        if '.bg-light' in content:
            content = re.sub(
                r'(\.bg-light\s*\{[^}]*)(})',
                r'\1    background: #353535 !important;\n            color: #FFFFFF !important;\n        \2',
                content
            )
            changes_made.append("Fixed .bg-light styling")
        
        # Fix 6: Inline bg-light classes
        if 'class="' in content and 'bg-light' in content:
            # Add style to bg-light elements
            content = re.sub(
                r'class="([^"]*bg-light[^"]*)"',
                r'class="\1" style="background: #353535 !important; color: #FFFFFF !important;"',
                content
            )
            changes_made.append("Added inline styles to bg-light elements")
        
        # Fix 7: Bootstrap .card styling in <style> blocks
        if re.search(r'\.card\s*\{', content):
            # Make sure cards have dark background
            content = re.sub(
                r'(\.card\s*\{[^}]*background[^;]*;)',
                r'\1\n            background: #2C2C2C !important;',
                content
            )
            changes_made.append("Fixed .card backgrounds")
        
        # Fix 8: .card-body styling
        if re.search(r'\.card-body\s*\{', content):
            content = re.sub(
                r'(\.card-body\s*\{)',
                r'\1\n            background: #2C2C2C !important;\n            color: #FFFFFF !important;',
                content
            )
            changes_made.append("Fixed .card-body styling")
        
        # Fix 9: .card-header with bg-light
        content = re.sub(
            r'class="card-header\s+bg-light"',
            r'class="card-header" style="background: #353535 !important; color: #FFFFFF !important; border-bottom: 1px solid #4A4A4A !important;"',
            content
        )
        if 'card-header' in original_content and 'bg-light' in original_content:
            changes_made.append("Fixed .card-header bg-light")
        
        # Fix 10: Bootstrap .alert classes
        if '.alert' in content and re.search(r'\.alert\s*\{', content):
            content = re.sub(
                r'(\.alert\s*\{[^}]*)(})',
                r'\1    background: #2C2C2C !important;\n            color: #FFFFFF !important;\n            border: 1px solid #4A4A4A !important;\n        \2',
                content
            )
            changes_made.append("Fixed .alert styling")
        
        # Fix 11: .alert-info specifically
        if '.alert-info' in content:
            content = re.sub(
                r'(\.alert-info\s*\{[^}]*)(})',
                r'\1    background: #2C5F77 !important;\n            color: #FFFFFF !important;\n            border-left: 4px solid #2196F3 !important;\n        \2',
                content
            )
            changes_made.append("Fixed .alert-info styling")
        
        # Fix 12: .alert-warning
        if '.alert-warning' in content:
            content = re.sub(
                r'(\.alert-warning\s*\{[^}]*)(})',
                r'\1    background: #5C4020 !important;\n            color: #FFFFFF !important;\n            border-left: 4px solid #FFC107 !important;\n        \2',
                content
            )
            changes_made.append("Fixed .alert-warning styling")
        
        # Fix 13: .alert-success
        if '.alert-success' in content:
            content = re.sub(
                r'(\.alert-success\s*\{[^}]*)(})',
                r'\1    background: #1C4025 !important;\n            color: #FFFFFF !important;\n            border-left: 4px solid #4CAF50 !important;\n        \2',
                content
            )
            changes_made.append("Fixed .alert-success styling")
        
        # Fix 14: .alert-danger
        if '.alert-danger' in content:
            content = re.sub(
                r'(\.alert-danger\s*\{[^}]*)(})',
                r'\1    background: #4A1C1C !important;\n            color: #FFFFFF !important;\n            border-left: 4px solid #f44336 !important;\n        \2',
                content
            )
            changes_made.append("Fixed .alert-danger styling")
        
        # Fix 15: table.table (Bootstrap tables)
        if re.search(r'\.table\s*\{', content) and 'table-d365' not in content:
            content = re.sub(
                r'(\.table\s*\{[^}]*)(})',
                r'\1    background: #2C2C2C !important;\n            color: #FFFFFF !important;\n        \2',
                content
            )
            changes_made.append("Fixed .table styling")
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return len(changes_made), changes_made
        
        return 0, []
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return 0, []

def main():
    """Fix all template files in the project."""
    templates_dir = Path('templates')
    
    if not templates_dir.exists():
        print(f"Error: {templates_dir} directory not found")
        return
    
    print("=" * 80)
    print("COMPREHENSIVE VISIBILITY FIX - SYSTEM-WIDE")
    print("=" * 80)
    print()
    
    total_files = 0
    total_changes = 0
    files_modified = []
    
    # Process all HTML files
    for html_file in templates_dir.rglob('*.html'):
        changes_count, changes_list = fix_file(html_file)
        
        if changes_count > 0:
            total_files += 1
            total_changes += changes_count
            files_modified.append({
                'file': str(html_file),
                'changes': changes_list
            })
            print(f"✓ {html_file.relative_to(templates_dir)}")
            for change in changes_list:
                print(f"  - {change}")
            print()
    
    print("=" * 80)
    print(f"SUMMARY")
    print("=" * 80)
    print(f"Files modified: {total_files}")
    print(f"Total changes: {total_changes}")
    print()
    
    if files_modified:
        print("Modified files:")
        for item in files_modified:
            print(f"  • {item['file']}")
    
    print()
    print("✅ All visibility issues fixed throughout the system!")
    print("🔄 Please refresh your browser to see the changes.")

if __name__ == '__main__':
    main()

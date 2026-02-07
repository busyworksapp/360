#!/usr/bin/env python3
"""
Fix all badge colors throughout the system - replace light backgrounds with high contrast colors
"""

import os
import re

# Define color replacements
replacements = [
    # Success (Green) - Paid, Delivered, Active, Completed
    (r'background:\s*#dff6dd;\s*color:\s*#4CAF50', 'background: #4CAF50 !important; color: #1C1C1C !important; font-weight: 600 !important'),
    
    # Warning/Pending (Amber/Gold)
    (r'background:\s*#fff4ce;\s*color:\s*#797673', 'background: #FFC107 !important; color: #1C1C1C !important; font-weight: 600 !important'),
    (r'background:\s*#fff4ce;\s*color:\s*#f7630c', 'background: #FFC107 !important; color: #1C1C1C !important; font-weight: 600 !important'),
    
    # Danger/Error (Red) - Failed, Cancelled, Overdue, Unpaid
    (r'background:\s*#fde7e9;\s*color:\s*#f44336', 'background: #f44336 !important; color: #FFFFFF !important; font-weight: 600 !important'),
    
    # Info/Processing (Blue) - Processing, Shipped, Sent
    (r'background:\s*#deecf9;\s*color:\s*#DAA520', 'background: #2196F3 !important; color: #FFFFFF !important; font-weight: 600 !important'),
    (r'background:\s*#deecf9;\s*color:\s*#004578', 'background: #2196F3 !important; color: #FFFFFF !important; font-weight: 600 !important'),
    (r'background:\s*#cfe4fa;\s*color:\s*#004578', 'background: #2196F3 !important; color: #FFFFFF !important; font-weight: 600 !important'),
    
    # With borders
    (r'background:\s*#dff6dd;\s*color:\s*#4CAF50;\s*border:\s*1px solid #4CAF50', 'background: #4CAF50 !important; color: #1C1C1C !important; font-weight: 600 !important; border: none !important'),
    (r'background:\s*#fff4ce;\s*color:\s*#797673;\s*border:\s*1px solid #797673', 'background: #FFC107 !important; color: #1C1C1C !important; font-weight: 600 !important; border: none !important'),
    (r'background:\s*#fde7e9;\s*color:\s*#f44336;\s*border:\s*1px solid #f44336', 'background: #f44336 !important; color: #FFFFFF !important; font-weight: 600 !important; border: none !important'),
    (r'background:\s*#deecf9;\s*color:\s*#DAA520;\s*border:\s*1px solid #DAA520', 'background: #2196F3 !important; color: #FFFFFF !important; font-weight: 600 !important; border: none !important'),
    
    # CSS rule versions (without semicolons at end)
    (r'background:\s*#dff6dd\s*(?=[;\n}])', 'background: #4CAF50 !important'),
    (r'background:\s*#fff4ce\s*(?=[;\n}])', 'background: #FFC107 !important'),
    (r'background:\s*#fde7e9\s*(?=[;\n}])', 'background: #f44336 !important'),
    (r'background:\s*#deecf9\s*(?=[;\n}])', 'background: #2196F3 !important'),
    (r'background:\s*#cfe4fa\s*(?=[;\n}])', 'background: #2196F3 !important'),
]

# Files to process (templates directory)
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

def fix_file(filepath):
    """Fix badge colors in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        # Apply all replacements
        for pattern, replacement in replacements:
            new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            if new_content != content:
                changes += len(re.findall(pattern, content, flags=re.IGNORECASE))
                content = new_content
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes
        
        return 0
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return 0

def main():
    """Process all template files"""
    total_files = 0
    total_changes = 0
    
    print("🎨 Fixing badge colors throughout the system...")
    print("-" * 60)
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                changes = fix_file(filepath)
                if changes > 0:
                    relative_path = os.path.relpath(filepath, templates_dir)
                    print(f"✅ {relative_path}: {changes} changes")
                    total_files += 1
                    total_changes += changes
    
    print("-" * 60)
    print(f"🎉 Complete! Fixed {total_files} files with {total_changes} total changes")
    print("\n💡 Refresh your browser (Ctrl + Shift + R) to see the changes!")

if __name__ == '__main__':
    main()

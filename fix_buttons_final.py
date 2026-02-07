import os
import re

def fix_buttons_and_commandbars(file_path):
    """Fix all button styling issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        # Fix command-bar backgrounds
        if 'command-bar' in content:
            content = re.sub(
                r'(\.command-bar[^{]*\{[^}]*?)background:\s*#[fF]{3,6}',
                r'\1background: #2C2C2C !important',
                content
            )
            content = re.sub(
                r'(\.command-bar[^{]*\{[^}]*?)background:\s*white',
                r'\1background: #2C2C2C !important',
                content
            )
            changes.append('command-bar backgrounds')
        
        # Fix search-box backgrounds
        if 'search-box' in content or 'search' in content.lower():
            content = re.sub(
                r'(\.search-box[^{]*\{[^}]*?)background:\s*#[fF]{3,6}',
                r'\1background: #353535 !important',
                content
            )
            content = re.sub(
                r'(input\[type[^{]*\{[^}]*?)background:\s*#[fF]{3,6}',
                r'\1background: #353535 !important; color: #FFFFFF !important',
                content
            )
            changes.append('search boxes')
        
        # Fix filter input styling
        content = re.sub(
            r'#filterInput\s*\{[^}]*\}',
            '''#filterInput {
                background: #353535 !important;
                color: #FFFFFF !important;
                border: 1px solid #4A4A4A !important;
                padding: 8px 12px;
            }''',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes
        return False, []
    
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False, []

def process_all():
    base_dir = r"c:\Users\4667.KevroAD\OneDrive - Barron (Pty) Ltd\Desktop\v\templates"
    
    print("=" * 80)
    print("FIXING BUTTONS AND COMMAND BARS")
    print("=" * 80)
    print()
    
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                all_files.append(os.path.join(root, file))
    
    fixed_count = 0
    for file_path in sorted(all_files):
        relative = file_path.replace(base_dir + os.sep, "")
        fixed, changes = fix_buttons_and_commandbars(file_path)
        if fixed:
            fixed_count += 1
            print(f"✓ {relative}")
            if changes:
                print(f"  └─ {', '.join(changes)}")
    
    print()
    print("=" * 80)
    print(f"✓ Fixed {fixed_count} files")
    print("=" * 80)
    print()
    print("🔘 All buttons now have:")
    print("   • Primary: Gold background (#DAA520) with dark text")
    print("   • Secondary: Gray background (#4A4A4A) with white text")
    print("   • Visible text with proper contrast")
    print("   • Command bars with dark backgrounds")
    print()
    print("🔄 REFRESH YOUR BROWSER!")

if __name__ == "__main__":
    process_all()

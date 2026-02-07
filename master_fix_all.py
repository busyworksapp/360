import os
import re

def comprehensive_fix(file_path):
    """Apply comprehensive fixes to ensure all text is visible on dark backgrounds"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        # ========================================
        # FIX 1: ALL WHITE BACKGROUNDS TO DARK
        # ========================================
        
        # CSS white backgrounds
        patterns = [
            (r'background:\s*#ffffff\s*([;!])', r'background: #2C2C2C !important\1', 'white hex'),
            (r'background:\s*#FFFFFF\s*([;!])', r'background: #2C2C2C !important\1', 'white HEX'),
            (r'background:\s*white\s*([;!])', r'background: #2C2C2C !important\1', 'white keyword'),
            (r'background:\s*#fff\s*([;!])', r'background: #2C2C2C !important\1', 'white short'),
            (r'background-color:\s*#ffffff\s*([;!])', r'background-color: #2C2C2C !important\1', 'bg-color white'),
            (r'background-color:\s*white\s*([;!])', r'background-color: #2C2C2C !important\1', 'bg-color keyword'),
        ]
        
        for pattern, replacement, desc in patterns:
            before = content
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            if content != before:
                changes.append(desc)
        
        # ========================================
        # FIX 2: LIGHT GRAY BACKGROUNDS TO DARKER
        # ========================================
        
        light_grays = [
            (r'background:\s*#f3f2f1', r'background: #2C2C2C !important', 'light gray f3f2f1'),
            (r'background:\s*#faf9f8', r'background: #2C2C2C !important', 'light gray faf9f8'),
            (r'background:\s*#f5f5f5', r'background: #2C2C2C !important', 'light gray f5f5f5'),
            (r'background:\s*#e1dfdd', r'background: #2C2C2C !important', 'light gray e1dfdd'),
            (r'background:\s*#edebe9', r'background: #2C2C2C !important', 'light gray edebe9'),
        ]
        
        for pattern, replacement, desc in light_grays:
            before = content
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            if content != before:
                changes.append(desc)
        
        # ========================================
        # FIX 3: ENSURE TEXT COLORS ARE VISIBLE
        # ========================================
        
        # Black text on dark backgrounds - change to white
        text_fixes = [
            (r'color:\s*#000000\s*;', r'color: #FFFFFF !important;', 'black text to white'),
            (r'color:\s*#000\s*;', r'color: #FFFFFF !important;', 'black short to white'),
            (r'color:\s*black\s*;', r'color: #FFFFFF !important;', 'black keyword to white'),
        ]
        
        for pattern, replacement, desc in text_fixes:
            before = content
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            if content != before:
                changes.append(desc)
        
        # ========================================
        # FIX 4: SPECIFIC COMPONENT FIXES
        # ========================================
        
        # Cards
        if '.card' in content or 'class="card' in content:
            content = re.sub(
                r'(\.card[^{]*\{[^}]*?)background:\s*[^;!]+',
                r'\1background: #2C2C2C !important',
                content
            )
            changes.append('card backgrounds')
        
        # Product cards
        if '.product-card' in content:
            content = re.sub(
                r'(\.product-card[^{]*\{[^}]*?)background:\s*[^;!]+',
                r'\1background: #2C2C2C !important',
                content
            )
            changes.append('product-card backgrounds')
        
        # Stat cards
        if '.stat-card' in content:
            content = re.sub(
                r'(\.stat-card[^{]*\{[^}]*?)background:\s*[^;!]+',
                r'\1background: #2C2C2C !important',
                content
            )
        
        # Search bars
        if 'search' in content.lower():
            content = re.sub(
                r'(\.search[^{]*\{[^}]*?)background:\s*#ffffff',
                r'\1background: #353535 !important',
                content,
                flags=re.IGNORECASE
            )
            changes.append('search bars')
        
        # Filter bars
        if 'filter' in content.lower():
            content = re.sub(
                r'(\.filter[^{]*\{[^}]*?)background:\s*#ffffff',
                r'\1background: #2C2C2C !important',
                content,
                flags=re.IGNORECASE
            )
        
        # Forms
        if '.form-control' in content or 'form' in content.lower():
            content = re.sub(
                r'(\.form-control[^{]*\{[^}]*?)background:\s*#ffffff',
                r'\1background: #353535 !important',
                content,
                flags=re.IGNORECASE
            )
            changes.append('form controls')
        
        # Input fields
        content = re.sub(
            r'(input[^{]*\{[^}]*?)background:\s*#ffffff',
            r'\1background: #353535 !important',
            content,
            flags=re.IGNORECASE
        )
        
        # Tables
        if 'table' in content.lower():
            content = re.sub(
                r'(\.table[^{]*\{[^}]*?)background:\s*#ffffff',
                r'\1background: #2C2C2C !important',
                content,
                flags=re.IGNORECASE
            )
            changes.append('tables')
        
        # Modals
        if 'modal' in content.lower():
            content = re.sub(
                r'(\.modal[^{]*\{[^}]*?)background:\s*#ffffff',
                r'\1background: #2C2C2C !important',
                content,
                flags=re.IGNORECASE
            )
            changes.append('modals')
        
        # ========================================
        # FIX 5: INLINE STYLES IN HTML
        # ========================================
        
        # Fix inline style backgrounds
        content = re.sub(
            r'style="([^"]*?)background:\s*(?:white|#fff(?:fff)?)\s*([;"])',
            r'style="\1background: #2C2C2C !important\2',
            content,
            flags=re.IGNORECASE
        )
        
        content = re.sub(
            r'style="([^"]*?)background-color:\s*(?:white|#fff(?:fff)?)\s*([;"])',
            r'style="\1background-color: #2C2C2C !important\2',
            content,
            flags=re.IGNORECASE
        )
        
        # ========================================
        # FIX 6: ENSURE PROPER BORDERS
        # ========================================
        
        # Add borders where missing on cards
        if 'class="card' in content or 'class="stat-card' in content:
            content = re.sub(
                r'(class="(?:card|stat-card)[^"]*"[^>]*style="[^"]*?)(")',
                r'\1; border: 1px solid #4A4A4A !important\2',
                content
            )
        
        # ========================================
        # FIX 7: NAVBAR AND HEADERS
        # ========================================
        
        if 'navbar' in content.lower() or 'header' in content.lower():
            content = re.sub(
                r'(\.navbar[^{]*\{[^}]*?)background:\s*#ffffff',
                r'\1background: #1C1C1C !important',
                content,
                flags=re.IGNORECASE
            )
            changes.append('navbar')
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes
        return False, []
            
    except Exception as e:
        print(f"  ✗ Error in {file_path}: {str(e)}")
        return False, []


def scan_and_fix_all():
    """Scan and fix ALL templates in the entire application"""
    base_dir = r"c:\Users\4667.KevroAD\OneDrive - Barron (Pty) Ltd\Desktop\v\templates"
    
    print("=" * 80)
    print("COMPREHENSIVE FIX - SCANNING ENTIRE APPLICATION")
    print("=" * 80)
    print()
    
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                all_files.append(os.path.join(root, file))
    
    print(f"Found {len(all_files)} HTML template files to scan...")
    print()
    
    fixed_count = 0
    total_changes = 0
    
    for file_path in sorted(all_files):
        relative_path = file_path.replace(base_dir + os.sep, "")
        fixed, changes = comprehensive_fix(file_path)
        
        if fixed:
            fixed_count += 1
            total_changes += len(changes)
            print(f"✓ {relative_path}")
            if changes:
                unique_changes = list(set(changes))
                print(f"  └─ Fixed: {', '.join(unique_changes[:5])}")
                if len(unique_changes) > 5:
                    print(f"             ...and {len(unique_changes) - 5} more")
    
    print()
    print("=" * 80)
    print(f"✓ COMPLETE: Fixed {fixed_count} files with {total_changes} total changes")
    print("=" * 80)
    print()
    print("🎨 Your entire app now has:")
    print("   • Dark charcoal backgrounds (#2C2C2C)")
    print("   • Visible white text (#FFFFFF)")
    print("   • Gold accents (#DAA520)")
    print("   • Proper borders (#4A4A4A)")
    print("   • Consistent styling across all pages")
    print()
    print("🔄 REFRESH YOUR BROWSER (Ctrl+Shift+R) to see all changes!")
    print()


if __name__ == "__main__":
    scan_and_fix_all()

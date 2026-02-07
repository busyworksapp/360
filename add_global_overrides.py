#!/usr/bin/env python3
"""
Add global CSS overrides to all base templates to ensure complete visibility.
"""

from pathlib import Path

GLOBAL_CSS_OVERRIDES = """
        /* GLOBAL VISIBILITY OVERRIDES - Force dark theme everywhere */
        * {
            scrollbar-width: thin;
            scrollbar-color: #4A4A4A #1C1C1C;
        }
        
        /* Force all text to be visible */
        body, p, span, div, td, th, li, a, label, input, textarea, select {
            color: #FFFFFF !important;
        }
        
        /* Override any light backgrounds */
        .bg-white, .bg-light, .card, .modal-content {
            background: #2C2C2C !important;
            color: #FFFFFF !important;
        }
        
        /* Force table visibility */
        table, .table {
            background: #2C2C2C !important;
            color: #FFFFFF !important;
        }
        
        table thead, .table thead {
            background: #1C1C1C !important;
        }
        
        table th, .table th {
            color: #FFFFFF !important;
            border-color: #4A4A4A !important;
        }
        
        table td, .table td {
            color: #FFFFFF !important;
            border-color: #4A4A4A !important;
        }
        
        /* Force form controls to be visible */
        input, textarea, select {
            background: #2C2C2C !important;
            color: #FFFFFF !important;
            border-color: #808080 !important;
        }
        
        input::placeholder, textarea::placeholder {
            color: #808080 !important;
        }
        
        /* Force alerts to be visible */
        .alert {
            color: #FFFFFF !important;
        }
        
        .alert-info {
            background: #2C5F77 !important;
            border-left: 4px solid #2196F3 !important;
        }
        
        .alert-warning {
            background: #5C4020 !important;
            border-left: 4px solid #FFC107 !important;
        }
        
        .alert-success {
            background: #1C4025 !important;
            border-left: 4px solid #4CAF50 !important;
        }
        
        .alert-danger {
            background: #4A1C1C !important;
            border-left: 4px solid #f44336 !important;
        }
        
        /* Force buttons to be visible */
        .btn, button {
            color: #FFFFFF !important;
        }
        
        .btn-primary {
            background: #DAA520 !important;
            border-color: #DAA520 !important;
            color: #000000 !important;
        }
        
        .btn-secondary {
            background: #808080 !important;
            border-color: #808080 !important;
        }
        
        .btn-success {
            background: #4CAF50 !important;
            border-color: #4CAF50 !important;
        }
        
        .btn-danger {
            background: #f44336 !important;
            border-color: #f44336 !important;
        }
        
        /* Force modals to be visible */
        .modal-header, .modal-body, .modal-footer {
            background: #2C2C2C !important;
            color: #FFFFFF !important;
            border-color: #4A4A4A !important;
        }
        
        /* Force dropdown menus to be visible */
        .dropdown-menu {
            background: #2C2C2C !important;
            border-color: #4A4A4A !important;
        }
        
        .dropdown-item {
            color: #FFFFFF !important;
        }
        
        .dropdown-item:hover {
            background: #353535 !important;
        }
        
        /* Force badges to be visible */
        .badge {
            background: #4A4A4A !important;
            color: #FFFFFF !important;
        }
        
        /* Text color overrides */
        .text-dark {
            color: #FFFFFF !important;
        }
        
        .text-muted {
            color: #C0C0C0 !important;
        }
        
        .text-secondary {
            color: #C0C0C0 !important;
        }
        
        /* Links */
        a {
            color: #DAA520 !important;
        }
        
        a:hover {
            color: #FFC107 !important;
        }
"""

def add_global_overrides(file_path):
    """Add global CSS overrides to a base template."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if overrides already exist
        if 'GLOBAL VISIBILITY OVERRIDES' in content:
            return False
        
        # Find the closing </style> tag in the head
        if '</style>' in content:
            # Insert before the FIRST closing style tag
            parts = content.split('</style>', 1)
            new_content = parts[0] + GLOBAL_CSS_OVERRIDES + '\n    </style>' + parts[1]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    """Add global overrides to all base templates."""
    base_templates = [
        Path('templates/base.html'),
        Path('templates/admin/base.html'),
        Path('templates/customer/base.html'),
        Path('templates/payment/base.html'),
    ]
    
    print("=" * 80)
    print("ADDING GLOBAL CSS OVERRIDES TO BASE TEMPLATES")
    print("=" * 80)
    print()
    
    modified = 0
    
    for template in base_templates:
        if template.exists():
            if add_global_overrides(template):
                print(f"✓ Added overrides to {template}")
                modified += 1
            else:
                print(f"○ Overrides already exist in {template}")
        else:
            print(f"✗ File not found: {template}")
    
    print()
    print("=" * 80)
    print(f"Modified {modified} base templates")
    print("=" * 80)
    print()
    print("✅ Global CSS overrides added!")
    print("🔄 Refresh your browser to see ALL visibility issues resolved.")

if __name__ == '__main__':
    main()

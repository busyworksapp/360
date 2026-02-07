import os
import re

# Define the comprehensive CSS override that will work across all templates
COMPREHENSIVE_CSS_FIX = """
        /* ========================================
           COMPREHENSIVE VISIBILITY & COLOR FIX
           ======================================== */
        
        /* Base colors - override everything */
        * {
            color: #FFFFFF !important;
        }
        
        body {
            background: #1C1C1C !important;
            color: #FFFFFF !important;
        }
        
        /* Headings */
        h1, h2, h3, h4, h5, h6,
        .h1, .h2, .h3, .h4, .h5, .h6 {
            color: #DAA520 !important;
        }
        
        /* Sidebar - complete override */
        .sidebar {
            background: #2C2C2C !important;
            border-right: 1px solid #4A4A4A !important;
        }
        
        .sidebar-header {
            background: #2C2C2C !important;
            border-bottom: 1px solid #4A4A4A !important;
        }
        
        .sidebar-header i {
            color: #DAA520 !important;
        }
        
        .sidebar-header .brand-text,
        .sidebar-header span {
            color: #FFFFFF !important;
        }
        
        .sidebar-item {
            color: #FFFFFF !important;
        }
        
        .sidebar-item i {
            color: #DAA520 !important;
        }
        
        .sidebar-item span {
            color: #FFFFFF !important;
        }
        
        .sidebar-item:hover {
            background: rgba(218, 165, 32, 0.15) !important;
        }
        
        .sidebar-item.active {
            background: rgba(218, 165, 32, 0.25) !important;
            border-left: 3px solid #DAA520 !important;
        }
        
        /* Tables - complete override */
        table,
        .table,
        .table-d365 {
            background: #2C2C2C !important;
            border: 1px solid #4A4A4A !important;
        }
        
        table thead,
        .table thead,
        .table-d365 thead {
            background: #1C1C1C !important;
        }
        
        table th,
        .table th,
        .table-d365 th {
            background: #1C1C1C !important;
            color: #DAA520 !important;
            border: 1px solid #4A4A4A !important;
            font-weight: 600 !important;
            padding: 12px !important;
        }
        
        table tbody,
        .table tbody,
        .table-d365 tbody {
            background: #2C2C2C !important;
        }
        
        table td,
        .table td,
        .table-d365 td {
            background: #353535 !important;
            color: #FFFFFF !important;
            border: 1px solid #4A4A4A !important;
            padding: 12px !important;
        }
        
        table tr:hover td,
        .table tr:hover td,
        .table-d365 tr:hover td {
            background: #404040 !important;
        }
        
        /* Links in tables */
        table a,
        .table a,
        .table-d365 a {
            color: #FFD700 !important;
            text-decoration: none !important;
        }
        
        table a:hover,
        .table a:hover,
        .table-d365 a:hover {
            color: #DAA520 !important;
            text-decoration: underline !important;
        }
        
        /* Cards */
        .card,
        .card-d365 {
            background: #2C2C2C !important;
            border: 1px solid #4A4A4A !important;
            color: #FFFFFF !important;
        }
        
        .card-header,
        .card-d365-header {
            background: #1C1C1C !important;
            color: #DAA520 !important;
            border-bottom: 1px solid #4A4A4A !important;
        }
        
        .card-body,
        .card-d365-body {
            background: #2C2C2C !important;
            color: #FFFFFF !important;
        }
        
        .card-footer {
            background: #1C1C1C !important;
            border-top: 1px solid #4A4A4A !important;
            color: #FFFFFF !important;
        }
        
        /* Stat cards */
        .stat-card {
            background: #2C2C2C !important;
            border: 1px solid #4A4A4A !important;
            color: #FFFFFF !important;
        }
        
        .stat-card h3,
        .stat-card .h3 {
            color: #DAA520 !important;
        }
        
        .stat-card p,
        .stat-card span,
        .stat-card div {
            color: #FFFFFF !important;
        }
        
        .stat-icon {
            color: #DAA520 !important;
        }
        
        /* Form controls */
        .form-control,
        input[type="text"],
        input[type="email"],
        input[type="password"],
        input[type="number"],
        input[type="date"],
        input[type="tel"],
        textarea,
        select {
            background: #353535 !important;
            color: #FFFFFF !important;
            border: 1px solid #4A4A4A !important;
        }
        
        .form-control:focus,
        input:focus,
        textarea:focus,
        select:focus {
            background: #404040 !important;
            border-color: #DAA520 !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 0 0.2rem rgba(218, 165, 32, 0.25) !important;
        }
        
        .form-control::placeholder,
        input::placeholder,
        textarea::placeholder {
            color: #808080 !important;
        }
        
        .form-label,
        label {
            color: #FFFFFF !important;
            font-weight: 500 !important;
        }
        
        .form-text {
            color: #C0C0C0 !important;
        }
        
        /* Select dropdowns */
        select option {
            background: #2C2C2C !important;
            color: #FFFFFF !important;
        }
        
        /* Buttons */
        .btn-primary {
            background: #DAA520 !important;
            border-color: #DAA520 !important;
            color: #1C1C1C !important;
            font-weight: 600 !important;
        }
        
        .btn-primary:hover,
        .btn-primary:focus {
            background: #C9A520 !important;
            border-color: #C9A520 !important;
            color: #1C1C1C !important;
        }
        
        .btn-secondary {
            background: #4A4A4A !important;
            border-color: #4A4A4A !important;
            color: #FFFFFF !important;
        }
        
        .btn-secondary:hover {
            background: #5A5A5A !important;
            border-color: #5A5A5A !important;
        }
        
        .btn-success {
            background: #4CAF50 !important;
            border-color: #4CAF50 !important;
            color: #FFFFFF !important;
        }
        
        .btn-danger {
            background: #DC3545 !important;
            border-color: #DC3545 !important;
            color: #FFFFFF !important;
        }
        
        .btn-warning {
            background: #FFC107 !important;
            border-color: #FFC107 !important;
            color: #1C1C1C !important;
        }
        
        .btn-info {
            background: #17A2B8 !important;
            border-color: #17A2B8 !important;
            color: #FFFFFF !important;
        }
        
        /* Badges */
        .badge {
            color: #1C1C1C !important;
            font-weight: 600 !important;
        }
        
        .badge-primary {
            background: #DAA520 !important;
        }
        
        .badge-success {
            background: #4CAF50 !important;
            color: #FFFFFF !important;
        }
        
        .badge-warning {
            background: #FFC107 !important;
        }
        
        .badge-danger {
            background: #DC3545 !important;
            color: #FFFFFF !important;
        }
        
        /* Status badges */
        .status-pending {
            background: #FFC107 !important;
            color: #1C1C1C !important;
        }
        
        .status-paid {
            background: #4CAF50 !important;
            color: #FFFFFF !important;
        }
        
        .status-cancelled {
            background: #DC3545 !important;
            color: #FFFFFF !important;
        }
        
        /* Alerts */
        .alert {
            border: 1px solid #4A4A4A !important;
        }
        
        .alert-success {
            background: #2C5530 !important;
            color: #FFFFFF !important;
            border-color: #4CAF50 !important;
        }
        
        .alert-danger {
            background: #5C2C2C !important;
            color: #FFFFFF !important;
            border-color: #DC3545 !important;
        }
        
        .alert-warning {
            background: #5C4C1C !important;
            color: #FFFFFF !important;
            border-color: #FFC107 !important;
        }
        
        .alert-info {
            background: #1C3C4C !important;
            color: #FFFFFF !important;
            border-color: #17A2B8 !important;
        }
        
        /* Navbar */
        .navbar {
            background: #1C1C1C !important;
            border-bottom: 1px solid #4A4A4A !important;
        }
        
        .navbar-brand {
            color: #DAA520 !important;
        }
        
        .navbar-brand:hover {
            color: #FFD700 !important;
        }
        
        .nav-link {
            color: #FFFFFF !important;
        }
        
        .nav-link:hover {
            color: #DAA520 !important;
        }
        
        /* Breadcrumb */
        .breadcrumb {
            background: transparent !important;
        }
        
        .breadcrumb-item {
            color: #FFFFFF !important;
        }
        
        .breadcrumb-item a {
            color: #DAA520 !important;
        }
        
        .breadcrumb-item.active {
            color: #C0C0C0 !important;
        }
        
        /* Content area */
        .content {
            background: #2C2C2C !important;
            color: #FFFFFF !important;
        }
        
        .content-header {
            border-bottom: 2px solid #DAA520 !important;
        }
        
        /* Page header */
        .page-header {
            color: #DAA520 !important;
            border-bottom: 2px solid #DAA520 !important;
        }
        
        /* Modals */
        .modal-content {
            background: #2C2C2C !important;
            border: 1px solid #4A4A4A !important;
        }
        
        .modal-header {
            background: #1C1C1C !important;
            border-bottom: 1px solid #4A4A4A !important;
            color: #DAA520 !important;
        }
        
        .modal-body {
            background: #2C2C2C !important;
            color: #FFFFFF !important;
        }
        
        .modal-footer {
            background: #1C1C1C !important;
            border-top: 1px solid #4A4A4A !important;
        }
        
        .modal-title {
            color: #DAA520 !important;
        }
        
        .close,
        .btn-close {
            color: #FFFFFF !important;
            opacity: 0.8 !important;
        }
        
        /* Pagination */
        .pagination .page-link {
            background: #353535 !important;
            border: 1px solid #4A4A4A !important;
            color: #FFFFFF !important;
        }
        
        .pagination .page-link:hover {
            background: #404040 !important;
            border-color: #DAA520 !important;
            color: #DAA520 !important;
        }
        
        .pagination .page-item.active .page-link {
            background: #DAA520 !important;
            border-color: #DAA520 !important;
            color: #1C1C1C !important;
        }
        
        /* Dropdown menus */
        .dropdown-menu {
            background: #2C2C2C !important;
            border: 1px solid #4A4A4A !important;
        }
        
        .dropdown-item {
            color: #FFFFFF !important;
        }
        
        .dropdown-item:hover {
            background: #353535 !important;
            color: #DAA520 !important;
        }
        
        /* List groups */
        .list-group-item {
            background: #2C2C2C !important;
            border: 1px solid #4A4A4A !important;
            color: #FFFFFF !important;
        }
        
        .list-group-item:hover {
            background: #353535 !important;
        }
        
        /* Tabs */
        .nav-tabs {
            border-bottom: 1px solid #4A4A4A !important;
        }
        
        .nav-tabs .nav-link {
            color: #FFFFFF !important;
            border: 1px solid transparent !important;
        }
        
        .nav-tabs .nav-link:hover {
            border-color: #4A4A4A !important;
            color: #DAA520 !important;
        }
        
        .nav-tabs .nav-link.active {
            background: #2C2C2C !important;
            border-color: #4A4A4A #4A4A4A #2C2C2C !important;
            color: #DAA520 !important;
        }
        
        /* Progress bars */
        .progress {
            background: #353535 !important;
        }
        
        .progress-bar {
            background: #DAA520 !important;
        }
        
        /* Tooltips */
        .tooltip-inner {
            background: #1C1C1C !important;
            color: #FFFFFF !important;
        }
        
        /* Links */
        a {
            color: #DAA520 !important;
            text-decoration: none !important;
        }
        
        a:hover {
            color: #FFD700 !important;
            text-decoration: underline !important;
        }
        
        /* Text colors */
        .text-muted {
            color: #C0C0C0 !important;
        }
        
        .text-primary {
            color: #DAA520 !important;
        }
        
        .text-success {
            color: #4CAF50 !important;
        }
        
        .text-danger {
            color: #DC3545 !important;
        }
        
        .text-warning {
            color: #FFC107 !important;
        }
        
        /* Background colors */
        .bg-light {
            background: #353535 !important;
        }
        
        .bg-dark {
            background: #1C1C1C !important;
        }
        
        /* Borders */
        .border {
            border-color: #4A4A4A !important;
        }
        
        /* HR */
        hr {
            border-color: #4A4A4A !important;
            opacity: 1 !important;
        }
"""

def add_css_fix_to_template(file_path):
    """Add comprehensive CSS fix to a template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already has comprehensive fix
        if 'COMPREHENSIVE VISIBILITY & COLOR FIX' in content:
            print(f"  ✓ Already has comprehensive fix: {file_path}")
            return False
        
        # Find the last </style> tag before </head>
        style_end_pattern = r'(\s*)</style>(\s*</head>)'
        
        if re.search(style_end_pattern, content):
            # Add the fix before </style>
            new_content = re.sub(
                style_end_pattern,
                rf'\1{COMPREHENSIVE_CSS_FIX}\1</style>\2',
                content,
                count=1
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✓ Added comprehensive fix: {file_path}")
            return True
        else:
            print(f"  ✗ No </style> tag found: {file_path}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error processing {file_path}: {str(e)}")
        return False

def main():
    base_dir = r"c:\Users\4667.KevroAD\OneDrive - Barron (Pty) Ltd\Desktop\v\templates"
    
    # Templates to fix
    templates = [
        os.path.join(base_dir, "base.html"),
        os.path.join(base_dir, "admin", "base.html"),
        os.path.join(base_dir, "customer", "base.html"),
    ]
    
    print("Adding comprehensive color fix to templates...")
    print("=" * 60)
    
    fixed_count = 0
    for template in templates:
        if os.path.exists(template):
            if add_css_fix_to_template(template):
                fixed_count += 1
        else:
            print(f"  ✗ File not found: {template}")
    
    print("=" * 60)
    print(f"✓ Fixed {fixed_count} template files")
    print("\nNext step: Hard refresh your browser (Ctrl+Shift+R)")

if __name__ == "__main__":
    main()

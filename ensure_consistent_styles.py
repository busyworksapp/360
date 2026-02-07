import os
import re

# This script ensures all pages have consistent styling by adding inline style blocks
# to pages that might need extra styling beyond what base templates provide

INLINE_STYLE_BLOCK = """
{% block extra_css %}
<style>
    /* Ensure consistent gold & charcoal theme */
    body { background: #1C1C1C !important; color: #FFFFFF !important; }
    .content { background: #2C2C2C !important; }
    
    /* Cards */
    .card, .card-d365 { background: #2C2C2C !important; border: 1px solid #4A4A4A !important; }
    .card-header, .card-d365-header { background: #1C1C1C !important; color: #DAA520 !important; }
    .card-body, .card-d365-body { background: #2C2C2C !important; color: #FFFFFF !important; }
    
    /* Tables */
    table, .table, .table-d365 { background: #2C2C2C !important; }
    table th, .table th, .table-d365 th { background: #1C1C1C !important; color: #DAA520 !important; border: 1px solid #4A4A4A !important; }
    table td, .table td, .table-d365 td { background: #353535 !important; color: #FFFFFF !important; border: 1px solid #4A4A4A !important; }
    
    /* Buttons */
    .btn-primary { background: #DAA520 !important; border-color: #DAA520 !important; color: #1C1C1C !important; }
    .btn-secondary { background: #4A4A4A !important; color: #FFFFFF !important; }
    .btn-success { background: #4CAF50 !important; color: #FFFFFF !important; }
    .btn-danger { background: #DC3545 !important; color: #FFFFFF !important; }
    
    /* Forms */
    .form-control, input, textarea, select { background: #353535 !important; color: #FFFFFF !important; border: 1px solid #4A4A4A !important; }
    .form-label, label { color: #FFFFFF !important; }
    
    /* Stat cards */
    .stat-card { background: #2C2C2C !important; border: 1px solid #4A4A4A !important; }
    .stat-card h3 { color: #DAA520 !important; }
    .stat-card p { color: #FFFFFF !important; }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 { color: #DAA520 !important; }
    
    /* Text */
    p, span, div, td, th { color: #FFFFFF !important; }
    
    /* Badges */
    .badge { font-weight: 600 !important; }
    .badge-warning, .status-pending { background: #FFC107 !important; color: #1C1C1C !important; }
    .badge-success, .status-paid { background: #4CAF50 !important; color: #FFFFFF !important; }
    .badge-danger, .status-cancelled { background: #DC3545 !important; color: #FFFFFF !important; }
</style>
{% endblock %}
"""

def add_extra_css_block(file_path):
    """Add extra CSS block to template if it doesn't have one"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip base templates
        if 'base.html' in os.path.basename(file_path):
            return False
            
        # Skip if it already has extra_css block
        if '{% block extra_css %}' in content:
            return False
        
        # Skip if it doesn't extend a base template
        if '{% extends' not in content:
            return False
        
        # Find the first {% block %} or add after {% extends %}
        if '{% block title %}' in content:
            # Add before the title block
            pattern = r'({% extends[^%]+%}\s*)'
            replacement = rf'\1\n{INLINE_STYLE_BLOCK}\n'
            new_content = re.sub(pattern, replacement, content, count=1)
        else:
            # Add after extends
            pattern = r'({% extends[^%]+%}\s*)'
            replacement = rf'\1\n{INLINE_STYLE_BLOCK}\n'
            new_content = re.sub(pattern, replacement, content, count=1)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def process_templates():
    """Process all template files"""
    base_dir = r"c:\Users\4667.KevroAD\OneDrive - Barron (Pty) Ltd\Desktop\v\templates"
    
    # Key templates to ensure have styling
    priority_templates = [
        # Admin templates
        "admin/dashboard.html",
        "admin/products.html",
        "admin/orders.html",
        "admin/invoices.html",
        "admin/customers.html",
        "admin/company.html",
        "admin/contacts.html",
        "admin/services.html",
        "admin/transactions.html",
        
        # Customer templates
        "customer/dashboard.html",
        "customer/orders.html",
        "customer/invoices.html",
        "customer/products.html",
        "customer/profile.html",
        "customer/checkout.html",
        "customer/transactions.html",
        
        # Payment templates
        "payment/select_method.html",
        "payment/status.html",
        "payment/admin_transactions.html",
        
        # Public templates
        "products.html",
        "services.html",
        "cart.html",
        "contact.html",
    ]
    
    print("Ensuring consistent styling across all templates...")
    print("=" * 70)
    
    added_count = 0
    for template in priority_templates:
        file_path = os.path.join(base_dir, template)
        if os.path.exists(file_path):
            if add_extra_css_block(file_path):
                print(f"  ✓ Added styling to: {template}")
                added_count += 1
            else:
                print(f"  - Already styled or skipped: {template}")
        else:
            print(f"  ✗ Not found: {template}")
    
    print("=" * 70)
    print(f"✓ Enhanced {added_count} template files with consistent styling")
    print("\nAll pages will now match the dashboard look!")

if __name__ == "__main__":
    process_templates()

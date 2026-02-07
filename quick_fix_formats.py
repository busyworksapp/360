#!/usr/bin/env python3
"""Quick fix for remaining %.2f formats"""

import re
from pathlib import Path

files_to_fix = [
    'templates/customer/checkout.html',
    'templates/customer/invoice_detail.html',
    'templates/customer/invoices.html',
    'templates/customer/orders.html',
    'templates/customer/pay_invoice.html',
    'templates/customer/transactions.html',
]

for filepath in files_to_fix:
    path = Path(filepath)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace %.2f with {:,.2f}
        new_content = content.replace('"%.2f"|format', '"{:,.2f}".format')
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Fixed {filepath}")
        else:
            print(f"⏭️  Skipped {filepath} (no changes)")

print("\n✅ Done!")

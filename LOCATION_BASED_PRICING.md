"""
LOCATION-BASED PRICING SYSTEM DOCUMENTATION
===========================================

Overview:
---------
The 360Degree Supply platform now supports location-based pricing with automatic
geographic detection. Customers in South Africa see prices in ZAR (South African
Rand), while customers outside South Africa see prices in USD (US Dollars).

This system ensures:
✓ Localized pricing based on geographic location
✓ Automatic currency detection from customer IP
✓ Transparent, non-negotiable pricing per location
✓ Admin control over both local and international prices
✓ Seamless customer experience (no price switching visible)


ARCHITECTURE
============

1. GEOLOCATION SERVICE (geolocation.py)
---------------------------------------
Detects customer location from IP address.

Key Functions:
- get_client_ip(): Extracts real client IP from request
- get_country_from_ip(ip_address): Determines country from IP
- is_local_customer(ip_address): Boolean check for South Africa
- get_customer_location(ip_address): Full location details

Features:
- Dual API fallback (ip-api.com → ipapi.co)
- Proxy/load balancer aware
- Localhost detection for development
- Comprehensive location data (city, region)

Integration:
```python
from geolocation import geolocation_service

location = geolocation_service.get_customer_location()
if location['is_local']:
    # SA customer
else:
    # International customer
```


2. PRICING SERVICE (pricing.py)
--------------------------------
Manages location-aware pricing logic and formatting.

Key Functions:
- get_customer_pricing_context(ip_address): Full pricing metadata
- get_product_price(product, ip_address): Price for specific product
- get_product_list_context(products, ip_address): Pricing for multiple products
- format_price(price, currency_code): Format with currency symbol
- validate_pricing_data(price_zar, price_usd): Validate pricing

Currency Handling:
- ZAR: Formatted as "R X,XXX.XX" (South African)
- USD: Formatted as "$X,XXX.XX" (International)

Integration:
```python
from pricing import pricing_service

# Get pricing context for current customer
context = pricing_service.get_customer_pricing_context()
# Returns:
# {
#   'is_local': True/False,
#   'country_code': 'ZA',
#   'currency_code': 'ZAR',
#   'currency_symbol': 'R'
# }

# Get specific product price
price_info = pricing_service.get_product_price(product)
# Returns:
# {
#   'price': 1234.50,
#   'currency_code': 'ZAR',
#   'currency_symbol': 'R',
#   'formatted_price': 'R 1,234.50'
# }

# Get pricing for multiple products
list_context = pricing_service.get_product_list_context(products)
# Returns: {
#   'pricing_context': {...},
#   'products': [
#     {'product': product, 'price': 1234.50, 'formatted_price': 'R 1,234.50'},
#     ...
#   ]
# }
```


3. PRODUCT MODEL UPDATES (models.py)
-------------------------------------
Product model now includes location-based pricing fields:

New Fields:
- price_zar: South African Rand pricing
- price_usd: US Dollar pricing
- price: Legacy field for backward compatibility

New Methods:
- get_price_for_location(is_local): Get appropriate price
- get_currency_for_location(is_local): Get currency code
- to_dict(is_local): Convert to dict with location-aware pricing

Example:
```python
product.get_price_for_location(is_local=True)  # Returns ZAR price
product.get_price_for_location(is_local=False) # Returns USD price
product.get_currency_for_location(is_local=True) # Returns 'ZAR'
```


ADMIN INTERFACE
===============

Admin Product Management:
- /admin/products: Lists all products with BOTH ZAR and USD prices
- /admin/products/add: Add new product with ZAR and USD prices
- /admin/products/<id>/edit: Edit product pricing for both currencies

Admin Form Fields:
- Local Price (ZAR): Price for South African customers
- International Price (USD): Price for customers outside SA
- Unit: Product unit (L, KG, etc.)
- Display Order: Product ordering on frontend

Validation:
- At least one price (ZAR or USD) is required
- Prices must be non-negative numbers
- Form shows validation error if requirements not met

Backward Compatibility:
- Existing products with only legacy "price" are automatically migrated
- Legacy prices are assigned to price_zar (local pricing)
- Admins should set price_usd for complete coverage


CUSTOMER EXPERIENCE
===================

Product Listing (/products):
- Shows location-aware pricing automatically
- Displays currency symbol (R or $)
- Shows location detection result
- All prices filtered for location

Example Display:
- SA Customer sees:
  • "Product A - R 1,234.50"
  • Currency: ZAR
  • Alert: "Displaying prices in South African Rand (ZAR) for South Africa"

- US Customer sees:
  • "Product A - $123.45"
  • Currency: USD
  • Alert: "Displaying prices in US Dollars (USD) for United States"

Cart (/cart):
- Shows location-detected currency throughout
- Prices formatted with appropriate symbol
- Location info displayed in alert
- Totals in customer's currency

Checkout:
- Pricing remains consistent with detected location
- No price changes during checkout
- Currency locks based on initial detection


DATABASE MIGRATION
==================

Migration Script: migrate_pricing.py

Run migration with:
```bash
python migrate_pricing.py
```

What it does:
1. Adds price_zar column if missing
2. Adds price_usd column if missing
3. Migrates existing prices to price_zar
4. Reports migration statistics

Output example:
```
✓ price_zar column added
✓ price_usd column added
✓ Migrated 6 products with legacy prices

✓ Location-based pricing migration completed successfully!
```


IMPLEMENTATION NOTES
====================

Location Detection:
- Happens on every product view/cart view
- Uses customer's real IP (not X-Forwarded-For if possible)
- Falls back to international (USD) if detection fails
- Cached with 5-minute timeout in some views

Price Display Logic:
- Template shows ONLY the price for customer's location
- Admin interface shows BOTH prices
- Currency symbols automatically applied
- No manual currency selection by customers

Fallback Behavior:
- If geolocation fails: Defaults to USD (international)
- If price not set: Uses legacy price field
- If no prices set: Shows 0.00 (shouldn't happen with validation)

Security:
- No customer IP stored permanently
- Only used for location lookup
- Location detection is optional enhancement
- Works without external IP detection


TESTING CHECKLIST
=================

Admin Testing:
□ Visit /admin/products
□ Verify both ZAR and USD prices display
□ Add new product with ZAR and USD prices
□ Edit existing product pricing
□ Verify validation prevents missing prices

Local Customer Testing (South Africa):
□ Visit /products page
□ Verify prices show in ZAR (R currency)
□ Verify price format: "R X,XXX.XX"
□ Add product to cart
□ Verify cart shows ZAR prices
□ Verify totals in ZAR

International Customer Testing:
□ Use VPN/proxy to test non-SA IP
□ Visit /products page
□ Verify prices show in USD ($)
□ Verify price format: "$X,XXX.XX"
□ Add product to cart
□ Verify cart shows USD prices
□ Verify totals in USD

Backward Compatibility:
□ Existing products with price field work
□ Products without price_zar/price_usd use legacy price
□ Migration successfully converts old prices


DEPLOYMENT NOTES
================

For Production:
1. Run migrate_pricing.py on production database
2. Ensure all products have at least one price (ZAR or USD)
3. Update existing products with both prices where applicable
4. Test with actual IP addresses from different countries

Railway Deployment:
1. Git push includes all migration scripts
2. Connect to Railway database
3. Run: python migrate_pricing.py
4. Verify products have proper pricing

Environmental Considerations:
- Geolocation APIs (ip-api.com, ipapi.co) are free but rate-limited
- For high-traffic apps, consider MaxMind GeoIP2 (requires account)
- Localhost (127.0.0.1) always defaults to ZA for testing


FUTURE ENHANCEMENTS
===================

Potential Improvements:
1. MaxMind GeoIP2 database integration
2. Exchange rate automation (ZAR ↔ USD)
3. Regional pricing beyond ZA/International
4. Customer pricing tier overrides
5. Tax calculation per country
6. Currency selection override for customers
7. Pricing history and analytics
8. A/B testing pricing by region


TROUBLESHOOTING
===============

Problem: Prices show incorrectly
Solution: Check geolocation service - verify IP detection works
         Check pricing context passed to template
         Verify product has prices set for location

Problem: Admin prices not showing both currencies
Solution: Ensure product has both price_zar and price_usd
         If empty, show dash (—) for missing price
         Migration should have populated price_zar

Problem: Migration failed
Solution: Check database permissions
         Verify SQLite/MySQL tables exist
         Try running with verbose logging

Problem: Location detection always shows unknown
Solution: Check internet connectivity
         Verify APIs accessible (ip-api.com, ipapi.co)
         Falls back to USD if detection fails
"""

# This file is documentation only
# Implementation is in: geolocation.py, pricing.py, models.py, app.py, templates/

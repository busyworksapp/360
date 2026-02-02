# Location-Based Pricing - Quick Start Guide

## What Changed?

Your e-commerce platform now automatically displays prices based on customer location:
- **South Africa**: Prices in ZAR (R)
- **International**: Prices in USD ($)

## For Administrators

### Managing Product Prices

1. **Go to Admin Dashboard** → Products
2. **Add or Edit Product**
3. **Set Two Prices:**
   - Local Price (ZAR): Price for South African customers
   - International Price (USD): Price for customers outside SA
4. **Save**

### Viewing All Prices

On the Products List page (/admin/products):
- See both ZAR and USD prices in one table
- ZAR prices show with "R" symbol
- USD prices show with "$" symbol
- Toggle prices and locations at a glance

## For Customers

### Automatic Detection

Customers **don't see any currency options**. They automatically get:
- ZAR prices if located in South Africa
- USD prices if located anywhere else

### Display Examples

**South African Customer sees:**
```
Product Name
R 1,500.00
per Liter
```

**International Customer sees:**
```
Product Name
$95.50
per Liter
```

## Technical Implementation

### Files Changed:
- `models.py` - Added price_zar, price_usd columns
- `geolocation.py` - Detects customer country from IP
- `pricing.py` - Handles price formatting and currency
- `app.py` - Routes updated with pricing logic
- `templates/` - Admin and customer templates updated
- `requirements.txt` - Added geoip2 dependency

### Database

Ran migration to add pricing columns:
```bash
python migrate_pricing.py
```

Existing products automatically migrated:
- Old "price" field → price_zar (local SA pricing)
- Set price_usd for international pricing

## How It Works

1. **Customer visits products page**
2. **Server detects location from IP address** (via ip-api.com)
3. **Server determines if customer is in South Africa**
4. **Product prices filtered to location** (ZAR or USD)
5. **Customer sees only appropriate prices** (no confusion)

## Testing

### To Test ZAR (Local) Pricing:
- Visit /products from South Africa
- Prices display in ZAR (R)
- Check cart to verify consistency

### To Test USD (International) Pricing:
- Use a VPN to a non-SA country, OR
- Wait for international customer to visit
- Prices display in USD ($)

## Important Notes

✓ **No customer choice**: Prices shown automatically, not selectable
✓ **Backward compatible**: Old products still work with legacy price field
✓ **Fallback**: If location detection fails, shows USD (international)
✓ **Admin sees both**: Admin can always see and edit both prices
✓ **Secure**: No customer IP stored permanently

## Adding New Products

1. Enter product name, description, etc.
2. **Set Local Price (ZAR)** - Required for SA customers
3. **Set International Price (USD)** - Required for other customers
4. Both prices required to cover all customers

## Admin URL Links

- Products List: `/admin/products`
- Add Product: `/admin/products/add`
- Edit Product: `/admin/products/<id>/edit`

## Troubleshooting

**Problem**: Admin form missing price fields
→ Refresh page or clear browser cache

**Problem**: Products showing $0.00
→ Check product has price_zar and/or price_usd set

**Problem**: Location detection not working
→ Check internet connection
→ Falls back to USD automatically

## Support

For issues with pricing:
1. Check product has both prices set
2. Verify database migration ran successfully
3. Inspect browser developer console for errors
4. Check geolocation APIs are accessible (ip-api.com, ipapi.co)

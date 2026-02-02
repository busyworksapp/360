"""
Pricing service for handling location-based pricing logic.
Manages ZAR (South African) and USD (International) pricing.
"""

from geolocation import geolocation_service
import logging

logger = logging.getLogger(__name__)

# Currency information
CURRENCIES = {
    'ZAR': {
        'code': 'ZAR',
        'symbol': 'R',
        'name': 'South African Rand',
        'locale': 'af_ZA'
    },
    'USD': {
        'code': 'USD',
        'symbol': '$',
        'name': 'US Dollar',
        'locale': 'en_US'
    }
}


class PricingService:
    """Service for managing location-based pricing."""
    
    def __init__(self):
        """Initialize the pricing service."""
        self.currencies = CURRENCIES
    
    def get_customer_pricing_context(self, ip_address=None):
        """
        Get complete pricing context for a customer.
        
        Args:
            ip_address (str): Optional IP address to determine location
            
        Returns:
            dict: Contains location, currency, and pricing info
        """
        # Get customer location
        location = geolocation_service.get_customer_location(ip_address)
        is_local = location.get('is_local', False)
        
        # Determine currency
        currency_code = 'ZAR' if is_local else 'USD'
        currency_info = self.currencies.get(currency_code)
        
        return {
            'is_local': is_local,
            'country_code': location.get('country_code'),
            'country_name': location.get('country_name'),
            'city': location.get('city'),
            'region': location.get('region'),
            'currency_code': currency_code,
            'currency_symbol': currency_info.get('symbol'),
            'currency_name': currency_info.get('name'),
            'location_detected': location.get('success', False)
        }
    
    def get_product_price(self, product, ip_address=None):
        """
        Get the appropriate price for a product based on customer location.
        
        Args:
            product: Product object or model instance
            ip_address (str): Optional IP address to determine location
            
        Returns:
            dict: Contains price, currency, and related info
        """
        context = self.get_customer_pricing_context(ip_address)
        is_local = context.get('is_local', False)
        
        # Get appropriate price from product
        price = product.get_price_for_location(is_local)
        
        return {
            'price': float(price) if price else 0.0,
            'currency_code': context.get('currency_code'),
            'currency_symbol': context.get('currency_symbol'),
            'is_local': is_local,
            'formatted_price': self.format_price(
                price,
                context.get('currency_code')
            )
        }
    
    def format_price(self, price, currency_code='ZAR'):
        """
        Format price for display with currency symbol.
        
        Args:
            price: Price amount (float or Decimal)
            currency_code (str): Currency code (ZAR or USD)
            
        Returns:
            str: Formatted price string (e.g., "R 1,234.50" or "$1,234.50")
        """
        if currency_code == 'USD':
            # US format: $1,234.50
            return f"${float(price):,.2f}"
        else:
            # South African format: R 1,234.50
            return f"R {float(price):,.2f}"
    
    def get_product_list_context(self, products, ip_address=None):
        """
        Get pricing context for a list of products.
        
        Args:
            products: List of product objects
            ip_address (str): Optional IP address to determine location
            
        Returns:
            dict: Contains pricing context and products with prices
        """
        pricing_context = self.get_customer_pricing_context(ip_address)
        is_local = pricing_context.get('is_local', False)
        
        products_with_prices = []
        for product in products:
            price = product.get_price_for_location(is_local)
            products_with_prices.append({
                'product': product,
                'price': float(price) if price else 0.0,
                'formatted_price': self.format_price(
                    price,
                    pricing_context.get('currency_code')
                )
            })
        
        return {
            'pricing_context': pricing_context,
            'products': products_with_prices,
            'currency_code': pricing_context.get('currency_code'),
            'currency_symbol': pricing_context.get('currency_symbol')
        }
    
    def validate_pricing_data(self, price_zar, price_usd):
        """
        Validate that pricing data is correct.
        
        Args:
            price_zar: Local price in ZAR
            price_usd: International price in USD
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Both prices should be non-negative
            if price_zar and float(price_zar) < 0:
                return False, "ZAR price cannot be negative"
            if price_usd and float(price_usd) < 0:
                return False, "USD price cannot be negative"
            
            # At least one price should be set
            if not price_zar and not price_usd:
                return False, "At least one price (ZAR or USD) is required"
            
            return True, None
        except (ValueError, TypeError):
            return False, "Prices must be valid numbers"
    
    def get_currency_symbol(self, currency_code='ZAR'):
        """
        Get currency symbol for given currency code.
        
        Args:
            currency_code (str): Currency code
            
        Returns:
            str: Currency symbol
        """
        currency_info = self.currencies.get(currency_code, {})
        return currency_info.get('symbol', currency_code)
    
    def get_currency_info(self, currency_code='ZAR'):
        """
        Get complete currency information.
        
        Args:
            currency_code (str): Currency code
            
        Returns:
            dict: Currency information
        """
        return self.currencies.get(currency_code, {})


# Create global instance
pricing_service = PricingService()


def get_customer_pricing_context(ip_address=None):
    """Convenience function to get pricing context."""
    return pricing_service.get_customer_pricing_context(ip_address)


def get_product_price(product, ip_address=None):
    """Convenience function to get product price."""
    return pricing_service.get_product_price(product, ip_address)


def format_price(price, currency_code='ZAR'):
    """Convenience function to format price."""
    return pricing_service.format_price(price, currency_code)


def get_product_list_context(products, ip_address=None):
    """Convenience function to get product list context."""
    return pricing_service.get_product_list_context(products, ip_address)

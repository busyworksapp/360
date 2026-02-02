"""
Geolocation service for detecting customer location based on IP address.
Supports both GeoIP2 and fallback methods.
"""

import requests
from flask import request
import logging

logger = logging.getLogger(__name__)

# List of South African country codes and identifiers
SOUTH_AFRICA_CODES = ['ZA', 'South Africa', 'za']


class GeolocationService:
    """Service for determining customer location from IP address."""
    
    def __init__(self):
        """Initialize the geolocation service."""
        self.sa_codes = SOUTH_AFRICA_CODES
    
    def get_client_ip(self):
        """
        Get the real client IP address from request.
        Handles proxies and load balancers.
        
        Returns:
            str: Client IP address
        """
        # Check for IP from behind a proxy
        if request.environ.get('HTTP_CF_CONNECTING_IP'):  # Cloudflare
            return request.environ.get('HTTP_CF_CONNECTING_IP')
        
        # Standard proxy header
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            # X-Forwarded-For can contain multiple IPs, take first
            xff = request.environ.get('HTTP_X_FORWARDED_FOR')
            return xff.split(',')[0].strip()
        
        if request.environ.get('HTTP_X_REAL_IP'):  # Nginx
            return request.environ.get('HTTP_X_REAL_IP')
        
        # Direct connection
        return request.remote_addr
    
    def get_country_from_ip(self, ip_address=None):
        """
        Determine country from IP address using free GeoIP service.
        Falls back to multiple APIs for redundancy.
        
        Args:
            ip_address (str): IP address to lookup. If None, uses client IP.
            
        Returns:
            dict: Contains 'country_code', 'country_name', 'success' keys
        """
        if not ip_address:
            ip_address = self.get_client_ip()
        
        # Skip lookup for localhost/development
        if ip_address in ['127.0.0.1', 'localhost', '::1']:
            return {
                'country_code': 'ZA',
                'country_name': 'South Africa',
                'success': True,
                'is_local': True,
                'dev_environment': True
            }
        
        # Try primary API: ip-api.com
        try:
            response = requests.get(
                f'http://ip-api.com/json/{ip_address}',
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'country_code': data.get('countryCode', '').upper(),
                        'country_name': data.get('country', ''),
                        'city': data.get('city', ''),
                        'region': data.get('regionName', ''),
                        'success': True,
                        'is_local': data.get('countryCode', '').upper() == 'ZA'
                    }
        except Exception as e:
            msg = f"Primary GeoIP lookup failed for {ip_address}: {e}"
            logger.warning(msg)
        
        # Fallback API: ipapi.co
        try:
            response = requests.get(
                f'https://ipapi.co/{ip_address}/json/',
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                country_code = data.get('country_code', '').upper()
                if country_code:
                    return {
                        'country_code': country_code,
                        'country_name': data.get('country_name', ''),
                        'city': data.get('city', ''),
                        'region': data.get('region', ''),
                        'success': True,
                        'is_local': country_code == 'ZA'
                    }
        except Exception as e:
            msg = f"Fallback GeoIP lookup failed for {ip_address}: {e}"
            logger.warning(msg)
        
        # If all lookups fail, default to international (USD)
        logger.warning(f"Could not determine country for IP: {ip_address}")
        return {
            'country_code': 'UNKNOWN',
            'country_name': 'Unknown',
            'success': False,
            'is_local': False,
            'error': 'Could not determine location'
        }
    
    def is_local_customer(self, ip_address=None):
        """
        Determine if customer is from South Africa.
        
        Args:
            ip_address (str): IP address to check. If None, uses client IP.
            
        Returns:
            bool: True if customer is from South Africa, False otherwise
        """
        result = self.get_country_from_ip(ip_address)
        return result.get('is_local', False)
    
    def get_customer_location(self, ip_address=None):
        """
        Get comprehensive location information for customer.
        
        Args:
            ip_address (str): IP address to lookup. If None, uses client IP.
            
        Returns:
            dict: Location information with is_local flag
        """
        result = self.get_country_from_ip(ip_address)
        result['is_local'] = result.get('country_code') == 'ZA'
        return result


# Create global instance
geolocation_service = GeolocationService()


def get_customer_location(ip_address=None):
    """
    Convenience function to get customer location.
    
    Args:
        ip_address (str): Optional IP address to lookup
        
    Returns:
        dict: Location information
    """
    return geolocation_service.get_customer_location(ip_address)


def is_local_customer(ip_address=None):
    """
    Convenience function to check if customer is local (South Africa).
    
    Args:
        ip_address (str): Optional IP address to check
        
    Returns:
        bool: True if customer is from South Africa
    """
    return geolocation_service.is_local_customer(ip_address)

"""
Cloudflare Cache Management Utility
Allows programmatic cache clearing after deployments
"""

import os
import requests
from typing import Optional, Dict, List

class CloudflareCache:
    """Manage Cloudflare cache purging"""
    
    def __init__(self):
        self.zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.base_url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}"
        
        if not self.zone_id:
            print("Warning: CLOUDFLARE_ZONE_ID not set. Cache purging disabled.")
        if not self.api_token:
            print("Warning: CLOUDFLARE_API_TOKEN not set. Cache purging disabled.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def purge_all(self) -> bool:
        """Purge all cached content
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.zone_id or not self.api_token:
            print("❌ Cloudflare credentials not configured")
            return False
        
        try:
            url = f"{self.base_url}/purge_cache"
            data = {"purge_everything": True}
            
            response = requests.post(url, json=data, headers=self._get_headers())
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Successfully purged all Cloudflare cache")
                    return True
                else:
                    errors = result.get('errors', [])
                    print(f"❌ Cache purge failed: {errors}")
                    return False
            else:
                print(f"❌ API request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error purging cache: {str(e)}")
            return False
    
    def purge_urls(self, urls: List[str]) -> bool:
        """Purge specific URLs from cache
        
        Args:
            urls: List of full URLs to purge (max 30 per request)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.zone_id or not self.api_token:
            print("❌ Cloudflare credentials not configured")
            return False
        
        if len(urls) > 30:
            print("⚠️  Warning: Can only purge 30 URLs at a time. Splitting requests...")
            # Split into chunks of 30
            for i in range(0, len(urls), 30):
                chunk = urls[i:i+30]
                if not self.purge_urls(chunk):
                    return False
            return True
        
        try:
            url = f"{self.base_url}/purge_cache"
            data = {"files": urls}
            
            response = requests.post(url, json=data, headers=self._get_headers())
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Successfully purged {len(urls)} URLs from cache")
                    return True
                else:
                    errors = result.get('errors', [])
                    print(f"❌ Cache purge failed: {errors}")
                    return False
            else:
                print(f"❌ API request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error purging URLs: {str(e)}")
            return False
    
    def purge_tags(self, tags: List[str]) -> bool:
        """Purge cache by tags (Enterprise only)
        
        Args:
            tags: List of cache tags to purge
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.zone_id or not self.api_token:
            print("❌ Cloudflare credentials not configured")
            return False
        
        try:
            url = f"{self.base_url}/purge_cache"
            data = {"tags": tags}
            
            response = requests.post(url, json=data, headers=self._get_headers())
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Successfully purged cache for tags: {', '.join(tags)}")
                    return True
                else:
                    errors = result.get('errors', [])
                    print(f"❌ Cache purge failed: {errors}")
                    return False
            else:
                print(f"❌ API request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error purging tags: {str(e)}")
            return False
    
    def purge_static_assets(self, domain: str = "https://www.360degreesupply.co.za") -> bool:
        """Purge common static assets after deployment
        
        Args:
            domain: Base domain URL
            
        Returns:
            bool: True if successful, False otherwise
        """
        static_urls = [
            f"{domain}/static/css/style.css",
            f"{domain}/static/js/table-functions.js",
            f"{domain}/",  # Homepage
        ]
        
        print(f"🔄 Purging static assets...")
        return self.purge_urls(static_urls)


# CLI usage
if __name__ == "__main__":
    import sys
    
    cache = CloudflareCache()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python cloudflare_cache.py all              # Purge all cache")
        print("  python cloudflare_cache.py static           # Purge static assets")
        print("  python cloudflare_cache.py urls <url1> <url2> ...  # Purge specific URLs")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "all":
        print("🔄 Purging all Cloudflare cache...")
        cache.purge_all()
    elif command == "static":
        cache.purge_static_assets()
    elif command == "urls":
        if len(sys.argv) < 3:
            print("❌ Please provide URLs to purge")
            sys.exit(1)
        urls = sys.argv[2:]
        cache.purge_urls(urls)
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

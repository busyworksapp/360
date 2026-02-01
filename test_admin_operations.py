#!/usr/bin/env python
"""
Comprehensive test script for 360Degree Supply admin operations.
Tests admin login, CRUD operations, and file uploads.
"""

import requests
import json
from io import BytesIO
from PIL import Image
import time

BASE_URL = 'http://127.0.0.1:5000'
ADMIN_EMAIL = 'admin@360degreesupply.co.za'
ADMIN_PASSWORD = 'admin123'

class AdminTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AdminTester/1.0',
            'Accept': 'application/json'
        })
        self.logged_in = False
        self.test_results = []

    def log_test(self, name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if message:
            print(f"   └─ {message}")
        self.test_results.append((name, passed))

    def create_test_image(self, filename="test.png"):
        """Create a test image in memory"""
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return ('image', img_io, 'image/png')

    def test_login(self):
        """Test admin login"""
        print("\n🔐 Testing Admin Login...")
        try:
            response = self.session.get(f'{BASE_URL}/admin/login')
            self.log_test("Login page loads", response.status_code == 200)
            
            login_data = {
                'email': ADMIN_EMAIL,
                'password': ADMIN_PASSWORD
            }
            response = self.session.post(
                f'{BASE_URL}/admin/login',
                data=login_data,
                allow_redirects=True
            )
            
            # Check if login was successful
            if response.status_code == 200 and '/admin' in response.url:
                self.logged_in = True
                self.log_test("Admin login successful", True)
            else:
                self.log_test("Admin login successful", False, 
                            f"Status: {response.status_code}, URL: {response.url}")
        except Exception as e:
            self.log_test("Admin login successful", False, str(e))

    def test_dashboard(self):
        """Test admin dashboard"""
        print("\n📊 Testing Admin Dashboard...")
        if not self.logged_in:
            self.log_test("Dashboard accessible", False, "Not logged in")
            return
        
        try:
            response = self.session.get(f'{BASE_URL}/admin')
            self.log_test("Dashboard loads", response.status_code == 200)
            
            # Check for expected content
            checks = [
                ('total_services' in response.text, "Services count visible"),
                ('total_products' in response.text, "Products count visible"),
                ('total_transactions' in response.text, "Transactions count visible"),
            ]
            
            for check, msg in checks:
                self.log_test(f"Dashboard: {msg}", check)
        except Exception as e:
            self.log_test("Dashboard loads", False, str(e))

    def test_services_management(self):
        """Test service CRUD operations"""
        print("\n🔧 Testing Services Management...")
        if not self.logged_in:
            self.log_test("View services", False, "Not logged in")
            return
        
        try:
            # Test viewing services list
            response = self.session.get(f'{BASE_URL}/admin/services')
            self.log_test("View services list", response.status_code == 200)
            
            # Test adding a service
            service_data = {
                'title': 'Test Service ' + str(int(time.time())),
                'description': 'This is a test service for automated testing',
                'icon': 'fas fa-cog',
                'order_position': 10,
                'is_active': 'on'
            }
            
            response = self.session.post(
                f'{BASE_URL}/admin/services/add',
                data=service_data,
                files={'image': self.create_test_image()},
                allow_redirects=True
            )
            
            service_added = response.status_code == 200 and 'services' in response.url
            self.log_test("Add new service", service_added, 
                         f"Status: {response.status_code}")
            
            # Get the list to find our new service
            response = self.session.get(f'{BASE_URL}/admin/services')
            service_in_list = service_data['title'] in response.text
            self.log_test("Service appears in list", service_in_list)
            
        except Exception as e:
            self.log_test("Services CRUD operations", False, str(e))

    def test_products_management(self):
        """Test product CRUD operations"""
        print("\n📦 Testing Products Management...")
        if not self.logged_in:
            self.log_test("View products", False, "Not logged in")
            return
        
        try:
            # Test viewing products list
            response = self.session.get(f'{BASE_URL}/admin/products')
            self.log_test("View products list", response.status_code == 200)
            
            # Test adding a product
            product_data = {
                'name': 'Test Product ' + str(int(time.time())),
                'description': 'This is a test product for automated testing',
                'category': 'Test Category',
                'specifications': 'Test specs',
                'price': '199.99',
                'unit': 'piece',
                'order_position': 10,
                'is_active': 'on'
            }
            
            response = self.session.post(
                f'{BASE_URL}/admin/products/add',
                data=product_data,
                files={'image': self.create_test_image()},
                allow_redirects=True
            )
            
            product_added = response.status_code == 200 and 'products' in response.url
            self.log_test("Add new product", product_added,
                         f"Status: {response.status_code}")
            
            # Get the list to find our new product
            response = self.session.get(f'{BASE_URL}/admin/products')
            product_in_list = product_data['name'] in response.text
            self.log_test("Product appears in list", product_in_list)
            
        except Exception as e:
            self.log_test("Products CRUD operations", False, str(e))

    def test_company_info(self):
        """Test company information management"""
        print("\n🏢 Testing Company Information...")
        if not self.logged_in:
            self.log_test("Company info page loads", False, "Not logged in")
            return
        
        try:
            # Test viewing company info
            response = self.session.get(f'{BASE_URL}/admin/company')
            self.log_test("Company info page loads", response.status_code == 200)
            
            # Test updating company info
            company_data = {
                'company_name': '360Degree Supply Updated ' + str(int(time.time())),
                'address': '123 Updated Street, Updated City',
                'phone': '+27 11 123 4567',
                'email': 'updated@360degreesupply.co.za',
                'description': 'Updated company description',
                'mission': 'Updated mission statement',
                'established_year': '2024'
            }
            
            response = self.session.post(
                f'{BASE_URL}/admin/company',
                data=company_data,
                files={'logo': self.create_test_image()},
                allow_redirects=True
            )
            
            company_updated = response.status_code == 200
            self.log_test("Update company info", company_updated,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Company information management", False, str(e))

    def test_public_pages(self):
        """Test public-facing pages"""
        print("\n🌐 Testing Public Pages...")
        
        pages = [
            ('Home', '/'),
            ('Services', '/services'),
            ('Products', '/products'),
            ('Payment', '/payment'),
        ]
        
        for name, path in pages:
            try:
                response = self.session.get(f'{BASE_URL}{path}')
                self.log_test(f"Public page: {name}", response.status_code == 200)
            except Exception as e:
                self.log_test(f"Public page: {name}", False, str(e))

    def test_contact_form(self):
        """Test contact form submission"""
        print("\n✉️  Testing Contact Form...")
        
        try:
            contact_data = {
                'name': 'Test User ' + str(int(time.time())),
                'email': 'test@example.com',
                'phone': '+27 11 999 8888',
                'message': 'This is a test contact form submission'
            }
            
            response = self.session.post(
                f'{BASE_URL}/api/contact',
                json=contact_data,
                headers={'Content-Type': 'application/json'}
            )
            
            form_works = response.status_code == 200
            self.log_test("Contact form submission", form_works,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Contact form submission", False, str(e))

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ Passed: {passed}/{total} ({percentage:.1f}%)")
        print("="*60)
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("\n❌ Failed tests:")
            for name, result in self.test_results:
                if not result:
                    print(f"   - {name}")

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("🚀 360Degree Supply Admin Panel Test Suite")
        print("="*60)
        
        self.test_login()
        self.test_dashboard()
        self.test_services_management()
        self.test_products_management()
        self.test_company_info()
        self.test_public_pages()
        self.test_contact_form()
        
        self.print_summary()


if __name__ == '__main__':
    tester = AdminTester()
    tester.run_all_tests()

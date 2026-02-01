#!/usr/bin/env python
"""Seed database with default admin user and sample data."""

import os
from dotenv import load_dotenv

load_dotenv()

from app import app, db
from models import User, CompanyInfo, Service, Product, HeroSection

def seed_database():
    """Seed database with initial data."""
    with app.app_context():
        print("🌱 Seeding database with initial data...")
        
        # Create default admin user
        admin_exists = User.query.filter_by(email='admin@360degreesupply.co.za').first()
        if not admin_exists:
            print("  Creating admin user...")
            admin = User(email='admin@360degreesupply.co.za', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("  ✓ Admin user created")
            print("    Email: admin@360degreesupply.co.za")
            print("    Password: admin123")
        else:
            print("  ✓ Admin user already exists")
        
        # Create default company info
        company = CompanyInfo.query.first()
        if not company:
            print("  Creating company information...")
            company = CompanyInfo(
                company_name='360Degree Supply (Pty) Ltd',
                address='Ei Ridge Office Park, 100 Elizabeth Road, Impala Park, Boksburg, 1459, Gauteng, South Africa',
                phone='+27 64 902 4363 / +27 71 181 4799',
                email='info@360degreesupply.co.za',
                description='A South African–based bulk fuel and mineral supply company providing reliable, end-to-end supply solutions to the mining, transport, agriculture, and industrial sectors.',
                mission='To be a trusted supply partner, providing certainty, transparency, and efficiency in every transaction.',
                established_year='2020'
            )
            db.session.add(company)
            db.session.commit()
            print("  ✓ Company information created")
        else:
            print("  ✓ Company information already exists")
        
        # Create sample hero sections
        hero_count = HeroSection.query.count()
        if hero_count == 0:
            print("  Creating hero sections...")
            hero1 = HeroSection(
                title='360Degree Supply – Your Trusted Mineral & Fuel Partner',
                subtitle='Reliable End-to-End Supply Solutions for Mining, Transport, and Industrial Sectors',
                description='South African-based bulk fuel and mineral supplier with Level 1 B-BBEE recognition. Specializing in Chrome ROM, Chrome Concentrate, Bulk Fuel, and Logistics.',
                cta_text='Request a Quote',
                cta_link='#contact',
                is_active=True,
                order_position=1
            )
            db.session.add(hero1)
            db.session.commit()
            print("  ✓ Hero sections created")
        else:
            print("  ✓ Hero sections already exist")
        
        # Create sample services
        service_count = Service.query.count()
        if service_count == 0:
            print("  Creating sample services...")
            services = [
                Service(
                    title='Chrome ROM & Chrome Concentrate Supply',
                    description='Reliable supply of high-quality chrome ROM and chrome concentrate for processors and manufacturers',
                    icon='gem',
                    order_position=1,
                    is_active=True
                ),
                Service(
                    title='Bulk Diesel & Fuel Supply',
                    description='Wholesale and resale of bulk diesel and all fuel grades nationwide',
                    icon='gas-pump',
                    order_position=2,
                    is_active=True
                ),
                Service(
                    title='Mineral Trading & Logistics',
                    description='Comprehensive mineral logistics and transport solutions across South Africa and SADC region',
                    icon='truck',
                    order_position=3,
                    is_active=True
                ),
                Service(
                    title='Mining & Industrial Support',
                    description='Expert mining and industrial support services with long-term supply agreements',
                    icon='hammer',
                    order_position=4,
                    is_active=True
                ),
                Service(
                    title='Offtake Agreements',
                    description='Secure offtake and long-term supply agreements with competitive pricing',
                    icon='handshake',
                    order_position=5,
                    is_active=True
                ),
                Service(
                    title='Secure Supply Chain',
                    description='Compliance-driven operations with partnerships to registered mines and processors',
                    icon='shield-alt',
                    order_position=6,
                    is_active=True
                )
            ]
            db.session.add_all(services)
            db.session.commit()
            print(f"  ✓ {len(services)} sample services created")
        else:
            print("  ✓ Services already exist")
        
        # Create sample products
        product_count = Product.query.count()
        if product_count == 0:
            print("  Creating sample products...")
            products = [
                Product(
                    name='Chrome ROM',
                    category='Minerals',
                    price=8500.00,
                    unit='ton',
                    description='High-quality chrome ROM ore for processing and manufacturing',
                    specifications='Grade: 42-46% Cr2O3, Certified, Direct from registered mines',
                    is_active=True,
                    order_position=1
                ),
                Product(
                    name='Chrome Concentrate',
                    category='Minerals',
                    price=12000.00,
                    unit='ton',
                    description='Concentrated chrome material ready for processing',
                    specifications='Grade: 48-52% Cr2O3, International standard, Bulk supply',
                    is_active=True,
                    order_position=2
                ),
                Product(
                    name='Bulk Diesel (Premium Grade)',
                    category='Fuel',
                    price=16.50,
                    unit='liter',
                    description='Premium-grade bulk diesel for industrial and transport use',
                    specifications='Ultra-low sulphur, EN 590 compliant, Wholesale pricing',
                    is_active=True,
                    order_position=3
                ),
                Product(
                    name='Bulk Petrol 95 (Unleaded)',
                    category='Fuel',
                    price=18.99,
                    unit='liter',
                    description='Unleaded petrol for transport and general industrial use',
                    specifications='RON 95, Lead-free, Quality assured, Bulk supply',
                    is_active=True,
                    order_position=4
                ),
                Product(
                    name='Logistics & Transport Services',
                    category='Services',
                    price=5000.00,
                    unit='shipment',
                    description='Secure logistics and transport solutions nationwide',
                    specifications='Nationwide coverage, SADC region available, Tracking included',
                    is_active=True,
                    order_position=5
                ),
                Product(
                    name='Long-Term Supply Agreement',
                    category='Contracts',
                    price=0.00,
                    unit='contract',
                    description='Customized long-term supply contracts with competitive rates',
                    specifications='Flexible terms, Offtake agreements, Deposit + milestone payments',
                    is_active=True,
                    order_position=6
                )
            ]
            db.session.add_all(products)
            db.session.commit()
            print(f"  ✓ {len(products)} sample products created")
        else:
            print("  ✓ Products already exist")
        
        print("\n✅ Database seeding complete!")
        print("\n📋 You can now login to the admin panel:")
        print("   URL: http://127.0.0.1:5000/admin")
        print("   Email: admin@360degreesupply.co.za")
        print("   Password: admin123")

if __name__ == '__main__':
    seed_database()

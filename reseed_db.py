#!/usr/bin/env python
"""Reset and reseed database with correct 360Degree Supply business info."""

import os
from dotenv import load_dotenv

load_dotenv()

from app import app, db
from models import (
    User, CompanyInfo, Service, Product, HeroSection, 
    PaymentMethod, PaymentTerm
)

def reset_and_seed_database():
    """Reset existing data and seed with correct information."""
    with app.app_context():
        print("🔄 Resetting database...")
        
        # Delete existing records (keep structure)
        try:
            HeroSection.query.delete()
            Service.query.delete()
            Product.query.delete()
            CompanyInfo.query.delete()
            db.session.commit()
            print("  ✓ Old data cleared")
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Error clearing data: {e}")
        
        print("\n🌱 Seeding database with 360Degree Supply information...\n")
        
        # Create company info with CORRECT details
        print("  📍 Creating company information...")
        company = CompanyInfo(
            company_name='360Degree Supply (Pty) Ltd',
            address='Ei Ridge Office Park, 100 Elizabeth Road, Impala Park, Boksburg, 1459, Gauteng, South Africa',
            phone='+27 64 902 4363 / +27 71 181 4799',
            email='info@360degreesupply.co.za',
            description='South African–based bulk fuel and mineral supply company providing reliable, end-to-end supply solutions to the mining, transport, agriculture, and industrial sectors.',
            mission='To be a trusted supply partner, providing certainty, transparency, and efficiency in every transaction.',
            established_year='2020'
        )
        db.session.add(company)
        db.session.commit()
        print("  ✓ Company information created")
        
        # Create hero section
        print("\n  🎯 Creating hero section...")
        hero1 = HeroSection(
            title='360Degree Supply – Your Trusted Mineral & Fuel Partner',
            subtitle='Reliable End-to-End Supply Solutions for Mining, Transport & Industrial Sectors',
            description='South African-based bulk fuel and mineral supplier with Level 1 B-BBEE recognition. Specializing in Chrome ROM, Chrome Concentrate, Bulk Fuel, and Logistics.',
            cta_text='Request a Quote',
            cta_link='#contact',
            is_active=True,
            order_position=1
        )
        db.session.add(hero1)
        db.session.commit()
        print("  ✓ Hero section created")
        
        # Create services matching actual business activities
        print("\n  🔧 Creating services...")
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
        print(f"  ✓ {len(services)} services created")
        
        # Create products matching actual offerings
        print("\n  📦 Creating products...")
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
        print(f"  ✓ {len(products)} products created")
        
        # Create payment methods
        print("\n  💳 Creating payment methods...")
        payment_methods = [
            PaymentMethod(
                name='EFT (Electronic Funds Transfer)',
                description='Bank-to-bank transfer with standard clearing time',
                icon='university',
                is_active=True,
                order_position=1
            ),
            PaymentMethod(
                name='PayFast (Instant EFT)',
                description='Instant payment confirmation for rapid processing',
                icon='bolt',
                is_active=True,
                order_position=2
            ),
            PaymentMethod(
                name='Stripe (Card Payments)',
                description='International card payments for global clients',
                icon='credit-card',
                is_active=True,
                order_position=3
            ),
            PaymentMethod(
                name='Bank Transfer (International)',
                description='Wire transfer for international buyers',
                icon='globe',
                is_active=True,
                order_position=4
            )
        ]
        db.session.add_all(payment_methods)
        db.session.commit()
        print(f"  ✓ {len(payment_methods)} payment methods created")
        
        # Create payment terms
        print("\n  ⏰ Creating payment terms...")
        payment_terms = [
            PaymentTerm(
                term_type='Spot Transaction (100% upfront)',
                description='Payment required before loading or delivery',
                order_position=1,
                is_active=True
            ),
            PaymentTerm(
                term_type='Deposit + Balance (Net 30)',
                description='Initial deposit with balance due within 30 days',
                order_position=2,
                is_active=True
            ),
            PaymentTerm(
                term_type='Net 14 Days',
                description='Full payment due within 14 days of invoice',
                order_position=3,
                is_active=True
            ),
            PaymentTerm(
                term_type='Net 60 Days',
                description='Extended payment terms for approved bulk buyers',
                order_position=4,
                is_active=True
            )
        ]
        db.session.add_all(payment_terms)
        db.session.commit()
        print(f"  ✓ {len(payment_terms)} payment terms created")
        
        print("\n" + "="*60)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("="*60)
        print("\n📋 Admin Credentials:")
        print("   Email: admin@360degreesupply.co.za")
        print("   Password: admin123")
        print("\n🔗 Access Admin Panel:")
        print("   URL: http://127.0.0.1:5000/admin")
        print("\n📞 Company Contact:")
        print("   360Degree Supply (Pty) Ltd")
        print("   +27 64 902 4363 / +27 71 181 4799")
        print("   info@360degreesupply.co.za")
        print("="*60)

if __name__ == '__main__':
    reset_and_seed_database()

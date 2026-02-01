"""Add sample testimonials to the database."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Testimonial


def seed_testimonials():
    """Add sample testimonials to database"""
    print("🌱 Adding sample testimonials...\n")

    with app.app_context():
        # Clear existing testimonials
        Testimonial.query.delete()

        testimonials = [
            {
                "client_name": "Thabo Dlamini",
                "company": "Impala Platinum Ltd",
                "position": "Operations Manager",
                "content":
                    "360Degree Supply has been instrumental in our mining "
                    "operations. Their reliability and fast delivery times "
                    "have helped us maintain production targets.",
                "rating": 5,
                "order_position": 1,
                "is_active": True
            },
            {
                "client_name": "Sarah Johnson",
                "company": "TransAfrica Logistics",
                "position": "Fleet Manager",
                "content":
                    "The bulk fuel supply service is exceptional. Competitive "
                    "pricing, consistent quality, and professional service. "
                    "Highly recommended!",
                "rating": 5,
                "order_position": 2,
                "is_active": True
            },
            {
                "client_name": "Kwame Mensah",
                "company": "Chrome Resources International",
                "position": "Procurement Director",
                "content":
                    "Working with 360Degree Supply for our chrome concentrate "
                    "orders has streamlined our supply chain significantly. "
                    "Excellent partnership.",
                "rating": 5,
                "order_position": 3,
                "is_active": True
            },
            {
                "client_name": "Maria Santos",
                "company": "Industrial Solutions SA",
                "position": "CEO",
                "content":
                    "Outstanding logistics support. They understand our "
                    "complex requirements and always deliver on time. "
                    "A true business partner.",
                "rating": 5,
                "order_position": 4,
                "is_active": True
            },
            {
                "client_name": "David Mkwanazi",
                "company": "Mining Innovations Corp",
                "position": "Supply Chain Lead",
                "content":
                    "The mining support services from 360Degree Supply are "
                    "comprehensive and cost-effective. They truly understand "
                    "the mining industry.",
                "rating": 5,
                "order_position": 5,
                "is_active": True
            },
            {
                "client_name": "Ahmed Osman",
                "company": "Desert Energy Trading",
                "position": "Trade Manager",
                "content":
                    "Their offtake agreements are transparent and fair. "
                    "Perfect for long-term supply arrangements. "
                    "Trustworthy and professional.",
                "rating": 5,
                "order_position": 6,
                "is_active": True
            },
        ]

        for testimonial_data in testimonials:
            testimonial = Testimonial(**testimonial_data)
            db.session.add(testimonial)
            print(f"   ✓ {testimonial_data['client_name']} - "
                  f"{testimonial_data['company']}")

        db.session.commit()
        print(f"\n✅ Added {len(testimonials)} testimonials!")


if __name__ == '__main__':
    seed_testimonials()

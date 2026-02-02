"""
Migration script to add price_zar and price_usd columns to products table.
This script handles the schema update for location-based pricing.
"""

from app import app, db
from models import Product
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_pricing():
    """
    Migrate existing product prices to new pricing model.
    - Adds price_zar and price_usd columns if they don't exist
    - Migrates existing price data to price_zar for backward compatibility
    """
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [
                col['name'] for col in inspector.get_columns('products')
            ]

            # Add price_zar column if missing
            if 'price_zar' not in columns:
                logger.info('Adding price_zar column...')
                with db.engine.connect() as conn:
                    if 'sqlite' in str(db.engine.url):
                        # SQLite approach
                        conn.execute(db.text(
                            'ALTER TABLE products ADD COLUMN '
                            'price_zar NUMERIC(10, 2)'
                        ))
                    else:
                        # MySQL approach
                        conn.execute(db.text(
                            'ALTER TABLE products ADD COLUMN '
                            'price_zar DECIMAL(10, 2)'
                        ))
                    conn.commit()
                logger.info('✓ price_zar column added')
            else:
                logger.info('✓ price_zar column already exists')

            # Add price_usd column if missing
            if 'price_usd' not in columns:
                logger.info('Adding price_usd column...')
                with db.engine.connect() as conn:
                    if 'sqlite' in str(db.engine.url):
                        # SQLite approach
                        conn.execute(db.text(
                            'ALTER TABLE products ADD COLUMN '
                            'price_usd NUMERIC(10, 2)'
                        ))
                    else:
                        # MySQL approach
                        conn.execute(db.text(
                            'ALTER TABLE products ADD COLUMN '
                            'price_usd DECIMAL(10, 2)'
                        ))
                    conn.commit()
                logger.info('✓ price_usd column added')
            else:
                logger.info('✓ price_usd column already exists')

            # Migrate existing price data
            logger.info('Migrating existing price data...')
            products = Product.query.all()
            migrated_count = 0

            for product in products:
                # Only migrate if legacy price exists but price_zar doesn't
                if (product.price and not product.price_zar and
                        not product.price_usd):
                    product.price_zar = product.price
                    migrated_count += 1

            if migrated_count > 0:
                db.session.commit()
                logger.info(
                    f'✓ Migrated {migrated_count} products with legacy '
                    'prices'
                )
            else:
                logger.info('✓ No legacy prices to migrate')

            logger.info('')
            logger.info('=' * 60)
            logger.info(
                '✓ Location-based pricing migration completed '
                'successfully!'
            )
            logger.info('=' * 60)
            logger.info('')
            logger.info('Next steps:')
            logger.info(
                '1. Set price_zar (ZAR) for South African customers'
            )
            logger.info(
                '2. Set price_usd (USD) for international customers'
            )
            logger.info('3. Visit /admin/products to manage pricing')
            logger.info('')

            return True

        except Exception as e:
            logger.error(f'✗ Migration failed: {str(e)}')
            logger.error('Make sure your database connection is working.')
            return False


if __name__ == '__main__':
    success = migrate_pricing()
    exit(0 if success else 1)

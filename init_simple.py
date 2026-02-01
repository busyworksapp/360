#!/usr/bin/env python
"""Initialize the database with all required tables - simplified version."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Flask to use a simpler config
os.environ['FLASK_ENV'] = 'development'

# Now import Flask and models
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', '').replace('mysql://', 'mysql+pymysql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

print("Initializing database connection...")
try:
    with app.app_context():
        print("Creating all tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
except Exception as e:
    print(f"✗ Error creating tables: {e}")
    sys.exit(1)

print("✅ Database initialization complete!")

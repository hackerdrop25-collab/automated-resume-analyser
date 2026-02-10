#!/usr/bin/env python
"""Quick script to create a test user"""
import os
import sys
from app import app, db
from models import User

def create_test_user():
    """Create a test user"""
    with app.app_context():
        email = "test@example.com"
        password = "password123"
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            print(f"User '{email}' already exists")
            return
        
        try:
            user = User(email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"[OK] Test user '{email}' created successfully with password 'password123'")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {e}")

if __name__ == '__main__':
    create_test_user()

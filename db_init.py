#!/usr/bin/env python
"""
Database initialization and management script
"""
import os
import sys
from datetime import datetime
from app import app, db
from models import User, Resume, JobDescription, AnalysisResult

def init_db():
    """Initialize the database"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully")


def drop_db():
    """Drop all database tables (WARNING: destructive operation)"""
    response = input("WARNING: This will delete all data. Are you sure? (yes/no): ")
    if response.lower() == 'yes':
        with app.app_context():
            print("Dropping all database tables...")
            db.drop_all()
            print("✓ All tables dropped")
    else:
        print("Operation cancelled")


def reset_db():
    """Reset the database (drop and recreate)"""
    response = input("WARNING: This will delete all data and recreate. Are you sure? (yes/no): ")
    if response.lower() == 'yes':
        with app.app_context():
            print("Resetting database...")
            db.drop_all()
            db.create_all()
            print("✓ Database reset successfully")
    else:
        print("Operation cancelled")


def create_test_user():
    """Create a test user"""
    with app.app_context():
        username = input("Enter username: ").strip()
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()
        
        if not username or not email or not password:
            print("All fields are required")
            return
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            print(f"User '{username}' already exists")
            return
        
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"✓ Test user '{username}' created successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {e}")


def show_stats():
    """Show database statistics"""
    with app.app_context():
        user_count = User.query.count()
        resume_count = Resume.query.count()
        job_desc_count = JobDescription.query.count()
        analysis_count = AnalysisResult.query.count()
        
        print("\n=== Database Statistics ===")
        print(f"Total Users: {user_count}")
        print(f"Total Resumes: {resume_count}")
        print(f"Total Job Descriptions: {job_desc_count}")
        print(f"Total Analyses: {analysis_count}")


def main():
    """Main CLI menu"""
    commands = {
        'init': ('Initialize database', init_db),
        'reset': ('Reset database (drop & recreate)', reset_db),
        'drop': ('Drop all tables', drop_db),
        'test-user': ('Create test user', create_test_user),
        'stats': ('Show database statistics', show_stats),
    }
    
    if len(sys.argv) < 2:
        print("Database Management Tool\n")
        print("Available commands:")
        for cmd, (desc, _) in commands.items():
            print(f"  python db_init.py {cmd:<15} - {desc}")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command not in commands:
        print(f"Unknown command: {command}")
        print(f"Available commands: {', '.join(commands.keys())}")
        sys.exit(1)
    
    commands[command][1]()


if __name__ == '__main__':
    main()

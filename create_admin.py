#!/usr/bin/env python3
"""
Script to create admin users for the NYC Nightlife API
"""
import sys
import getpass
from database import Database

def main():
    print("NYC Nightlife API - Create Admin User")
    print("=" * 40)
    
    db = Database()
    
    username = input("Username: ").strip()
    if not username:
        print("Username cannot be empty!")
        sys.exit(1)
    
    email = input("Email (optional): ").strip() or None
    full_name = input("Full Name (optional): ").strip() or None
    
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")
    
    if password != confirm_password:
        print("Passwords do not match!")
        sys.exit(1)
    
    if len(password) < 8:
        print("Password must be at least 8 characters long!")
        sys.exit(1)
    
    if db.create_admin_user(username, password, email, full_name):
        print(f"\n✓ Admin user '{username}' created successfully!")
    else:
        print(f"\n✗ Failed to create admin user. Username or email might already exist.")
        sys.exit(1)

if __name__ == "__main__":
    main()
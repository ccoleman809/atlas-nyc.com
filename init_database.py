#!/usr/bin/env python3
"""
Atlas-NYC Database Initialization Script
Initializes all required tables and creates sample data for launch
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import json

def init_core_tables(cursor):
    """Initialize core venue and content tables"""
    
    # Venues table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            neighborhood TEXT NOT NULL,
            instagram_handle TEXT,
            venue_type TEXT NOT NULL,
            address TEXT,
            description TEXT,
            busy_nights TEXT,
            price_range TEXT,
            photo TEXT,
            latitude REAL,
            longitude REAL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (created_by) REFERENCES admin_users (id)
        )
    ''')
    
    # Content table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venue_id INTEGER NOT NULL,
            content_type TEXT NOT NULL,
            media_url TEXT,
            media_type TEXT,
            caption TEXT,
            crowd_level TEXT,
            urgency TEXT,
            latitude REAL,
            longitude REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            created_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (venue_id) REFERENCES venues (id),
            FOREIGN KEY (created_by) REFERENCES admin_users (id)
        )
    ''')

def init_admin_tables(cursor):
    """Initialize admin and security tables"""
    
    # Admin users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            full_name TEXT,
            hashed_password TEXT NOT NULL,
            disabled BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            role TEXT DEFAULT 'admin'
        )
    ''')
    
    # API keys table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (created_by) REFERENCES admin_users (id)
        )
    ''')
    
    # Audit log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id INTEGER,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES admin_users (id)
        )
    ''')

def init_analytics_tables(cursor):
    """Initialize analytics tables"""
    
    # Analytics events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            venue_id INTEGER,
            content_id INTEGER,
            user_session TEXT,
            ip_address TEXT,
            user_agent TEXT,
            referrer TEXT,
            properties TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (venue_id) REFERENCES venues (id),
            FOREIGN KEY (content_id) REFERENCES content (id)
        )
    ''')
    
    # User sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            referrer TEXT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            page_views INTEGER DEFAULT 0,
            duration INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Daily venue stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_venue_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venue_id INTEGER NOT NULL,
            date DATE NOT NULL,
            views INTEGER DEFAULT 0,
            unique_visitors INTEGER DEFAULT 0,
            content_views INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            favorites INTEGER DEFAULT 0,
            UNIQUE(venue_id, date),
            FOREIGN KEY (venue_id) REFERENCES venues (id)
        )
    ''')
    
    # Daily content stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_content_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            venue_id INTEGER NOT NULL,
            date DATE NOT NULL,
            views INTEGER DEFAULT 0,
            unique_visitors INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            engagement_time INTEGER DEFAULT 0,
            UNIQUE(content_id, date),
            FOREIGN KEY (content_id) REFERENCES content (id),
            FOREIGN KEY (venue_id) REFERENCES venues (id)
        )
    ''')
    
    # Search analytics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_term TEXT NOT NULL,
            search_type TEXT,
            results_count INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Geographic stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS geographic_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            estimated_location TEXT,
            venue_id INTEGER,
            date DATE DEFAULT (date('now')),
            views INTEGER DEFAULT 1,
            FOREIGN KEY (venue_id) REFERENCES venues (id)
        )
    ''')
    
    # Performance metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            metadata TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

def create_indexes(cursor):
    """Create database indexes for performance"""
    
    indexes = [
        # Core table indexes
        "CREATE INDEX IF NOT EXISTS idx_venues_neighborhood ON venues(neighborhood)",
        "CREATE INDEX IF NOT EXISTS idx_venues_type ON venues(venue_type)",
        "CREATE INDEX IF NOT EXISTS idx_venues_active ON venues(is_active)",
        "CREATE INDEX IF NOT EXISTS idx_content_venue ON content(venue_id)",
        "CREATE INDEX IF NOT EXISTS idx_content_timestamp ON content(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_content_expires ON content(expires_at)",
        
        # Analytics indexes
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON analytics_events(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_venue ON analytics_events(venue_id)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_content ON analytics_events(content_id)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_session ON analytics_events(user_session)",
        "CREATE INDEX IF NOT EXISTS idx_daily_venue_stats_date ON daily_venue_stats(date)",
        "CREATE INDEX IF NOT EXISTS idx_daily_content_stats_date ON daily_content_stats(date)",
        "CREATE INDEX IF NOT EXISTS idx_user_sessions_session ON user_sessions(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_sessions_activity ON user_sessions(last_activity)",
        
        # Admin indexes
        "CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username)",
        "CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(key)",
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)

def insert_sample_data(cursor):
    """Insert sample venue data for launch"""
    
    sample_venues = [
        {
            'name': 'Sky Lounge',
            'neighborhood': 'SoHo',
            'venue_type': 'lounge',
            'address': '123 Broadway, New York, NY 10013',
            'description': 'Elevated cocktails with stunning city views in the heart of SoHo. Experience sophisticated nightlife with craft cocktails and a chic atmosphere.',
            'busy_nights': 'Thursday, Friday, Saturday',
            'price_range': '$$$',
            'instagram_handle': 'skyloungenyc',
            'latitude': 40.7223,
            'longitude': -74.0030
        },
        {
            'name': 'Underground NYC',
            'neighborhood': 'East Village',
            'venue_type': 'club',
            'address': '456 St Marks Pl, New York, NY 10009',
            'description': 'Dark, intimate club featuring underground electronic music and creative cocktails. A hidden gem in the East Village nightlife scene.',
            'busy_nights': 'Friday, Saturday',
            'price_range': '$$',
            'instagram_handle': 'undergroundnyc',
            'latitude': 40.7281,
            'longitude': -73.9847
        },
        {
            'name': 'Brooklyn Bowl',
            'neighborhood': 'Williamsburg',
            'venue_type': 'bar',
            'address': '61 Wythe Ave, Brooklyn, NY 11249',
            'description': 'Bowling, live music, and craft beer in a converted warehouse. Perfect for groups looking for entertainment and great drinks.',
            'busy_nights': 'Wednesday, Friday, Saturday',
            'price_range': '$$',
            'instagram_handle': 'brooklynbowl',
            'latitude': 40.7216,
            'longitude': -73.9586
        },
        {
            'name': 'Meatpacking Social',
            'neighborhood': 'Meatpacking District',
            'venue_type': 'rooftop',
            'address': '789 14th St, New York, NY 10014',
            'description': 'Rooftop venue with panoramic city views, craft cocktails, and upscale dining. The perfect spot for special occasions.',
            'busy_nights': 'Thursday, Friday, Saturday, Sunday',
            'price_range': '$$$$',
            'instagram_handle': 'meatpackingsocial',
            'latitude': 40.7408,
            'longitude': -74.0072
        },
        {
            'name': 'LES Dive Bar',
            'neighborhood': 'Lower East Side',
            'venue_type': 'bar',
            'address': '321 Ludlow St, New York, NY 10002',
            'description': 'Authentic NYC dive bar experience with cheap drinks, pool tables, and live music. A true Lower East Side institution.',
            'busy_nights': 'Every night',
            'price_range': '$',
            'instagram_handle': 'lesdivebar',
            'latitude': 40.7205,
            'longitude': -73.9897
        }
    ]
    
    for venue in sample_venues:
        cursor.execute('''
            INSERT INTO venues (name, neighborhood, venue_type, address, description, 
                              busy_nights, price_range, instagram_handle, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            venue['name'], venue['neighborhood'], venue['venue_type'],
            venue['address'], venue['description'], venue['busy_nights'],
            venue['price_range'], venue['instagram_handle'],
            venue['latitude'], venue['longitude']
        ))

def create_admin_user(cursor):
    """Create default admin user"""
    from auth import get_password_hash
    
    # Default admin credentials (change in production!)
    username = "admin"
    password = "AtlasNYC2024!"  # Change this!
    email = "admin@atlas-nyc.com"
    full_name = "Atlas NYC Administrator"
    
    hashed_password = get_password_hash(password)
    
    try:
        cursor.execute('''
            INSERT INTO admin_users (username, email, full_name, hashed_password)
            VALUES (?, ?, ?, ?)
        ''', (username, email, full_name, hashed_password))
        print(f"✓ Created admin user: {username}")
        print(f"✓ Default password: {password}")
        print("⚠️  IMPORTANT: Change this password after first login!")
    except sqlite3.IntegrityError:
        print(f"✓ Admin user '{username}' already exists")

def main():
    """Main database initialization function"""
    
    db_path = "nightlife.db"
    
    print("🚀 Initializing Atlas-NYC Database...")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Initialize all tables
        print("📋 Creating core tables...")
        init_core_tables(cursor)
        
        print("👑 Creating admin tables...")
        init_admin_tables(cursor)
        
        print("📊 Creating analytics tables...")
        init_analytics_tables(cursor)
        
        print("⚡ Creating database indexes...")
        create_indexes(cursor)
        
        print("🏢 Inserting sample venue data...")
        insert_sample_data(cursor)
        
        print("👤 Creating default admin user...")
        create_admin_user(cursor)
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ Database initialization completed successfully!")
        print(f"📁 Database file: {Path(db_path).absolute()}")
        print("🎯 Ready to launch Atlas-NYC!")
        
        print("\n📝 Next steps:")
        print("1. Change the default admin password")
        print("2. Update the BASE_URL in seo_utils.py")
        print("3. Configure your domain and SSL certificates")
        print("4. Start the server: python secure_api_server.py")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
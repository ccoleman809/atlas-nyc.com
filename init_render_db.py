#!/usr/bin/env python3
"""
Initialize database for Render deployment
Supports both SQLite (development) and PostgreSQL (production)
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from config import settings
from venue_db import VenueDatabase
from datetime import datetime

def is_postgres():
    """Check if we're using PostgreSQL"""
    return settings.DATABASE_URL.startswith('postgresql://')

def init_postgres_db():
    """Initialize PostgreSQL database"""
    print("🐘 Initializing PostgreSQL database...")
    
    # Parse DATABASE_URL
    db_url = settings.DATABASE_URL
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Create tables
        print("📊 Creating tables...")
        
        # Venues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venues (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                neighborhood VARCHAR(100) NOT NULL,
                instagram_handle VARCHAR(100) NOT NULL UNIQUE,
                venue_type VARCHAR(50) NOT NULL,
                address TEXT,
                description TEXT,
                busy_nights VARCHAR(50),
                price_range VARCHAR(10),
                latitude REAL,
                longitude REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index on venues
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_venues_neighborhood ON venues(neighborhood);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_venues_type ON venues(venue_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_venues_instagram ON venues(instagram_handle);")
        
        # Content table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id SERIAL PRIMARY KEY,
                venue_id INTEGER NOT NULL,
                content_type VARCHAR(50) NOT NULL,
                caption TEXT,
                file_path TEXT,
                crowd_level VARCHAR(20),
                urgency VARCHAR(20),
                latitude REAL,
                longitude REAL,
                expires_at TIMESTAMP,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (venue_id) REFERENCES venues (id) ON DELETE CASCADE
            );
        """)
        
        # Create index on content
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_venue_id ON content(venue_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_type ON content(content_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_timestamp ON content(timestamp);")
        
        # Admin users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Analytics events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(50) NOT NULL,
                venue_id INTEGER,
                user_agent TEXT,
                ip_address INET,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB
            );
        """)
        
        # API keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP
            );
        """)
        
        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                action VARCHAR(100) NOT NULL,
                table_name VARCHAR(50),
                record_id INTEGER,
                admin_username VARCHAR(100),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details JSONB
            );
        """)
        
        conn.commit()
        print("✅ PostgreSQL database initialized successfully!")
        
        # Check if we have any venues
        cursor.execute("SELECT COUNT(*) FROM venues")
        venue_count = cursor.fetchone()[0]
        print(f"📊 Current venue count: {venue_count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing PostgreSQL: {e}")
        return False

def migrate_sqlite_to_postgres():
    """Migrate data from SQLite to PostgreSQL"""
    print("🔄 Migrating data from SQLite to PostgreSQL...")
    
    # Check if SQLite database exists
    if not os.path.exists('nightlife.db'):
        print("⚠️  No SQLite database found to migrate")
        return
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect('nightlife.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to PostgreSQL
        postgres_conn = psycopg2.connect(settings.DATABASE_URL)
        postgres_cursor = postgres_conn.cursor()
        
        # Migrate venues
        sqlite_cursor.execute("SELECT * FROM venues")
        venues = sqlite_cursor.fetchall()
        
        # Get column names
        sqlite_cursor.execute("PRAGMA table_info(venues)")
        columns = [col[1] for col in sqlite_cursor.fetchall()]
        
        migrated_venues = 0
        for venue in venues:
            try:
                # Insert into PostgreSQL (excluding id to use auto-increment)
                postgres_cursor.execute("""
                    INSERT INTO venues (name, neighborhood, instagram_handle, venue_type, 
                                      address, description, busy_nights, price_range)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (instagram_handle) DO NOTHING
                """, venue[1:9])  # Skip id, take next 8 columns
                migrated_venues += 1
            except Exception as e:
                print(f"⚠️  Skipped venue {venue[1]}: {e}")
        
        postgres_conn.commit()
        print(f"✅ Migrated {migrated_venues} venues")
        
        # Close connections
        sqlite_conn.close()
        postgres_conn.close()
        
    except Exception as e:
        print(f"❌ Migration error: {e}")

def main():
    """Main initialization function"""
    print("🚀 Atlas-NYC Database Initialization")
    print("=" * 50)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database URL: {settings.DATABASE_URL[:50]}...")
    
    if is_postgres():
        # Initialize PostgreSQL
        if init_postgres_db():
            # Try to migrate SQLite data if available
            migrate_sqlite_to_postgres()
    else:
        # Use existing SQLite initialization
        print("💾 Using SQLite database...")
        db = VenueDatabase()
        print("✅ SQLite database ready")
    
    print("\n✨ Database initialization complete!")

if __name__ == "__main__":
    main()
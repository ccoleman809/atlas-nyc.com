#!/usr/bin/env python3
"""
Database optimization script for Atlas-NYC
Adds indexes and optimizes database performance
"""

import sqlite3
import time
from datetime import datetime

def optimize_database(db_path="nightlife.db"):
    """Add indexes and optimize database for production"""
    
    print(f"🚀 Optimizing database: {db_path}")
    print(f"Started at: {datetime.now()}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable query optimization
    cursor.execute("PRAGMA optimize")
    
    # Add indexes for venues table
    indexes = [
        # Venues indexes
        ("idx_venues_neighborhood", "venues", "neighborhood"),
        ("idx_venues_venue_type", "venues", "venue_type"),
        ("idx_venues_instagram", "venues", "instagram_handle"),
        ("idx_venues_name", "venues", "name"),
        ("idx_venues_price_range", "venues", "price_range"),
        
        # Content indexes
        ("idx_content_venue_id", "content", "venue_id"),
        ("idx_content_type", "content", "content_type"),
        ("idx_content_created", "content", "created_at"),
        ("idx_content_expires", "content", "expires_at"),
        
        # Admin users indexes
        ("idx_admin_username", "admin_users", "username"),
        ("idx_admin_email", "admin_users", "email"),
        
        # Analytics indexes
        ("idx_analytics_event_type", "analytics_events", "event_type"),
        ("idx_analytics_timestamp", "analytics_events", "timestamp"),
        ("idx_analytics_venue_id", "analytics_events", "venue_id"),
        
        # Audit log indexes
        ("idx_audit_action", "audit_log", "action"),
        ("idx_audit_admin_id", "audit_log", "admin_id"),
        ("idx_audit_timestamp", "audit_log", "timestamp"),
        
        # API keys indexes
        ("idx_api_keys_key", "api_keys", "key"),
        ("idx_api_keys_active", "api_keys", "is_active"),
    ]
    
    # Create indexes
    created_count = 0
    for index_name, table, column in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})")
            print(f"✅ Created index: {index_name}")
            created_count += 1
        except sqlite3.Error as e:
            print(f"⚠️  Error creating index {index_name}: {e}")
    
    # Create composite indexes for common queries
    composite_indexes = [
        ("idx_venues_neighborhood_type", "venues", "(neighborhood, venue_type)"),
        ("idx_content_venue_created", "content", "(venue_id, created_at DESC)"),
        ("idx_analytics_type_timestamp", "analytics_events", "(event_type, timestamp DESC)"),
    ]
    
    for index_name, table, columns in composite_indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table} {columns}")
            print(f"✅ Created composite index: {index_name}")
            created_count += 1
        except sqlite3.Error as e:
            print(f"⚠️  Error creating composite index {index_name}: {e}")
    
    # Analyze tables for query optimization
    tables = ["venues", "content", "admin_users", "analytics_events", "audit_log", "api_keys"]
    for table in tables:
        try:
            cursor.execute(f"ANALYZE {table}")
            print(f"📊 Analyzed table: {table}")
        except sqlite3.Error:
            pass
    
    # Vacuum to optimize storage
    print("\n🧹 Vacuuming database...")
    cursor.execute("VACUUM")
    
    # Get database statistics
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    size_bytes = cursor.fetchone()[0]
    size_mb = size_bytes / (1024 * 1024)
    
    # Get index count
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
    total_indexes = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database optimization complete!")
    print(f"📈 Created {created_count} new indexes")
    print(f"📊 Total indexes: {total_indexes}")
    print(f"💾 Database size: {size_mb:.2f} MB")
    print(f"⏱️  Completed at: {datetime.now()}")

def create_performance_views(db_path="nightlife.db"):
    """Create optimized views for common queries"""
    
    print("\n🔧 Creating performance views...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # View for active content with venue info
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS active_content_with_venues AS
        SELECT 
            c.*,
            v.name as venue_name,
            v.neighborhood,
            v.instagram_handle,
            v.venue_type
        FROM content c
        JOIN venues v ON c.venue_id = v.id
        WHERE c.expires_at IS NULL OR c.expires_at > datetime('now')
        ORDER BY c.created_at DESC
    """)
    
    # View for venue analytics
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS venue_analytics_summary AS
        SELECT 
            v.id,
            v.name,
            v.neighborhood,
            COUNT(DISTINCT a.id) as total_events,
            COUNT(DISTINCT CASE WHEN a.event_type = 'venue_view' THEN a.id END) as views,
            COUNT(DISTINCT CASE WHEN a.event_type = 'venue_search' THEN a.id END) as searches
        FROM venues v
        LEFT JOIN analytics_events a ON v.id = a.venue_id
        GROUP BY v.id
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Performance views created!")

if __name__ == "__main__":
    # Run optimization
    optimize_database()
    create_performance_views()
    
    print("\n💡 Performance tips:")
    print("1. Consider migrating to PostgreSQL for production")
    print("2. Enable connection pooling in your application")
    print("3. Use prepared statements for repeated queries")
    print("4. Monitor slow queries and optimize as needed")
    print("5. Consider implementing Redis caching for hot data")
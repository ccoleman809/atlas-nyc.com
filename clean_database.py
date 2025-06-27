#!/usr/bin/env python3
"""
Clean and merge database, removing duplicates
"""

import sqlite3
import os
from venue_db import VenueDatabase, Venue

def clean_and_merge_database():
    """Clean database by removing duplicates and keeping the best version of each venue"""
    
    # Backup current database
    if os.path.exists('nightlife.db'):
        os.rename('nightlife.db', 'nightlife_backup.db')
        print("✅ Created backup: nightlife_backup.db")
    
    # Create new clean database
    db = VenueDatabase()
    
    # Connect to backup to read all venues
    conn = sqlite3.connect('nightlife_backup.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, neighborhood, instagram_handle, venue_type, 
               address, description, busy_nights, price_range
        FROM venues
        ORDER BY id
    """)
    
    all_venues = cursor.fetchall()
    conn.close()
    
    # Track unique venues by name + neighborhood
    unique_venues = {}
    
    for row in all_venues:
        venue_id, name, neighborhood, instagram_handle, venue_type, address, description, busy_nights, price_range = row
        
        # Create unique key
        key = f"{name.lower()}_{neighborhood.lower()}"
        
        # If duplicate, keep the one with more complete data
        if key in unique_venues:
            existing = unique_venues[key]
            # Count non-null fields
            existing_score = sum(1 for field in [existing.address, existing.description, 
                                                existing.busy_nights, existing.price_range] if field)
            new_score = sum(1 for field in [address, description, busy_nights, price_range] if field)
            
            # Keep the one with more data, or the newer one if equal
            if new_score > existing_score:
                unique_venues[key] = Venue(
                    name=name,
                    neighborhood=neighborhood,
                    instagram_handle=instagram_handle,
                    venue_type=venue_type,
                    address=address,
                    description=description,
                    busy_nights=busy_nights,
                    price_range=price_range
                )
                print(f"🔄 Updated {name} with better data")
        else:
            unique_venues[key] = Venue(
                name=name,
                neighborhood=neighborhood,
                instagram_handle=instagram_handle,
                venue_type=venue_type,
                address=address,
                description=description,
                busy_nights=busy_nights,
                price_range=price_range
            )
    
    # Add all unique venues to new database
    added_count = 0
    for venue in unique_venues.values():
        venue_id = db.add_venue(venue)
        if venue_id > 0:
            added_count += 1
            print(f"✅ Added: {venue.name} ({venue.neighborhood})")
    
    print(f"\n📊 Summary:")
    print(f"Original venues: {len(all_venues)}")
    print(f"Unique venues: {len(unique_venues)}")
    print(f"Duplicates removed: {len(all_venues) - len(unique_venues)}")
    print(f"Total venues in clean database: {added_count}")

if __name__ == "__main__":
    print("🧹 Cleaning and merging database...")
    clean_and_merge_database()
    print("✅ Database cleanup complete!")
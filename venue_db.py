import sqlite3
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Venue:
    """Data model for nightlife venues"""
    name: str
    neighborhood: str
    instagram_handle: str
    venue_type: str  # 'dive_bar', 'dance_club', 'rooftop', 'cocktail_lounge', etc.
    address: Optional[str] = None
    description: Optional[str] = None
    busy_nights: Optional[str] = None  # 'Thu,Fri,Sat' or similar
    price_range: Optional[str] = None  # '$', '$$', '$$$'
    venue_id: Optional[int] = None
    created_at: Optional[str] = None

class VenueDatabase:
    """Manages the venue database operations"""
    
    def __init__(self, db_path: str = "nightlife.db"):
        self.db_path = db_path
        self.create_tables()
    
    def create_tables(self):
        """Create the venues table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS venues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                neighborhood TEXT NOT NULL,
                instagram_handle TEXT UNIQUE NOT NULL,
                venue_type TEXT NOT NULL,
                address TEXT,
                description TEXT,
                busy_nights TEXT,
                price_range TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_venue(self, venue: Venue) -> int:
        """Add a new venue to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO venues (name, neighborhood, instagram_handle, venue_type, 
                                  address, description, busy_nights, price_range)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (venue.name, venue.neighborhood, venue.instagram_handle, 
                  venue.venue_type, venue.address, venue.description, 
                  venue.busy_nights, venue.price_range))
            
            venue_id = cursor.lastrowid
            conn.commit()
            print(f"✅ Added venue: {venue.name} (ID: {venue_id})")
            return venue_id
            
        except sqlite3.IntegrityError:
            print(f"❌ Venue with Instagram handle @{venue.instagram_handle} already exists")
            return -1
        finally:
            conn.close()
    
    def get_all_venues(self) -> List[Venue]:
        """Get all venues from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM venues ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        
        venues = []
        for row in rows:
            venue = Venue(
                venue_id=row[0],
                name=row[1],
                neighborhood=row[2],
                instagram_handle=row[3],
                venue_type=row[4],
                address=row[5],
                description=row[6],
                busy_nights=row[7],
                price_range=row[8],
                created_at=row[9]
            )
            venues.append(venue)
        
        return venues
    
    def get_venues_by_neighborhood(self, neighborhood: str) -> List[Venue]:
        """Get venues filtered by neighborhood"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM venues WHERE neighborhood = ? ORDER BY name', (neighborhood,))
        rows = cursor.fetchall()
        conn.close()
        
        venues = []
        for row in rows:
            venue = Venue(
                venue_id=row[0],
                name=row[1],
                neighborhood=row[2],
                instagram_handle=row[3],
                venue_type=row[4],
                address=row[5],
                description=row[6],
                busy_nights=row[7],
                price_range=row[8],
                created_at=row[9]
            )
            venues.append(venue)
        
        return venues
    
    def display_venues(self, venues: List[Venue] = None):
        """Display venues in a nice format"""
        if venues is None:
            venues = self.get_all_venues()
        
        if not venues:
            print("No venues found.")
            return
        
        print(f"\n📍 Found {len(venues)} venues:")
        print("-" * 80)
        
        for venue in venues:
            print(f"🏢 {venue.name}")
            print(f"   📍 {venue.neighborhood} | @{venue.instagram_handle}")
            print(f"   🎭 {venue.venue_type.replace('_', ' ').title()}")
            if venue.busy_nights:
                print(f"   🗓️  Busy: {venue.busy_nights}")
            if venue.price_range:
                print(f"   💰 {venue.price_range}")
            print()

if __name__ == "__main__":
    # Initialize the database
    db = VenueDatabase()
    
    # Example venues to get you started
    sample_venues = [
        Venue(
            name="House of Yes",
            neighborhood="Bushwick",
            instagram_handle="houseofyes",
            venue_type="dance_club",
            description="Performance art meets nightclub",
            busy_nights="Thu,Fri,Sat",
            price_range="$$"
        ),
        Venue(
            name="Mood Ring",
            neighborhood="Bushwick",
            instagram_handle="moodringnyc",
            venue_type="cocktail_lounge",
            description="Queer-friendly cocktail bar",
            busy_nights="Fri,Sat,Sun",
            price_range="$$"
        )
    ]
    
    # Add sample venues
    print("Adding sample venues...")
    for venue in sample_venues:
        db.add_venue(venue)
    
    # Display all venues
    db.display_venues()

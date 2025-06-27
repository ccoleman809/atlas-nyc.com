#!/usr/bin/env python3
"""
Initialize the database with NYC venue data
"""

from venue_db import VenueDatabase, Venue

def init_database():
    """Initialize database with sample NYC venues"""
    db = VenueDatabase()
    
    # Sample NYC venues
    venues = [
        Venue(
            name="House of Yes",
            neighborhood="Bushwick",
            instagram_handle="houseofyes",
            venue_type="nightclub",
            address="2 Wyckoff Ave, Brooklyn, NY 11237",
            description="Creative nightclub and performance venue known for themed parties and immersive experiences",
            busy_nights="Thu,Fri,Sat",
            price_range="$$$"
        ),
        Venue(
            name="Brooklyn Bowl",
            neighborhood="Williamsburg",
            instagram_handle="brooklynbowl",
            venue_type="live_music_venue",
            address="61 Wythe Ave, Brooklyn, NY 11249",
            description="Bowling alley, music venue, and restaurant serving comfort food",
            busy_nights="Fri,Sat,Sun",
            price_range="$$"
        ),
        Venue(
            name="Death & Co",
            neighborhood="East Village",
            instagram_handle="deathandcompany",
            venue_type="cocktail_bar",
            address="433 E 6th St, New York, NY 10009",
            description="Pioneering cocktail bar with innovative drinks and intimate atmosphere",
            busy_nights="Thu,Fri,Sat",
            price_range="$$$"
        ),
        Venue(
            name="Le Bain",
            neighborhood="Meatpacking",
            instagram_handle="lebainstandardny",
            venue_type="rooftop_bar",
            address="444 W 13th St, New York, NY 10014",
            description="Rooftop disco and bar at The Standard High Line with panoramic city views",
            busy_nights="Fri,Sat",
            price_range="$$$$"
        ),
        Venue(
            name="Beauty & Essex",
            neighborhood="Lower East Side",
            instagram_handle="beautyandessex",
            venue_type="lounge",
            address="146 Essex St, New York, NY 10002",
            description="Upscale lounge hidden behind a pawn shop facade, serving cocktails and small plates",
            busy_nights="Thu,Fri,Sat",
            price_range="$$$"
        ),
        Venue(
            name="The Box",
            neighborhood="Lower East Side",
            instagram_handle="theboxnyc",
            venue_type="nightclub",
            address="189 Chrystie St, New York, NY 10002",
            description="Theatrical nightclub with burlesque performances and late-night entertainment",
            busy_nights="Thu,Fri,Sat",
            price_range="$$$$"
        ),
        Venue(
            name="Marquee",
            neighborhood="Chelsea",
            instagram_handle="marqueeny",
            venue_type="nightclub",
            address="289 10th Ave, New York, NY 10001",
            description="High-energy nightclub with world-class DJs and VIP bottle service",
            busy_nights="Fri,Sat",
            price_range="$$$$"
        ),
        Venue(
            name="Please Don't Tell",
            neighborhood="East Village",
            instagram_handle="pdtnyc",
            venue_type="cocktail_bar",
            address="113 St Marks Pl, New York, NY 10009",
            description="Hidden speakeasy accessed through a phone booth in a hot dog shop",
            busy_nights="Fri,Sat",
            price_range="$$$"
        )
    ]
    
    # Add venues to database
    added_count = 0
    for venue in venues:
        venue_id = db.add_venue(venue)
        if venue_id > 0:
            added_count += 1
            print(f"✅ Added: {venue.name}")
        else:
            print(f"⚠️ Skipped (already exists): {venue.name}")
    
    print(f"\n📊 Total venues added: {added_count}")
    print(f"📊 Total venues in database: {len(db.get_all_venues())}")

if __name__ == "__main__":
    print("🏗️ Initializing NYC venue database...")
    init_database()
    print("✅ Database initialization complete!")
#!/usr/bin/env python3
"""
Import popular NYC nightlife venues into Atlas-NYC database
"""

from venue_db import VenueDatabase, Venue
import googlemaps
from config import settings
from datetime import datetime
import time

# Popular NYC nightlife venues by neighborhood
NYC_VENUES = [
    # Manhattan - Lower East Side
    {
        "name": "Pianos",
        "neighborhood": "Lower East Side",
        "instagram_handle": "pianosnyc",
        "venue_type": "live_music_venue",
        "address": "158 Ludlow St, New York, NY 10002",
        "description": "Iconic LES venue with live music and DJ nights",
        "busy_nights": "Thu,Fri,Sat",
        "price_range": "$$"
    },
    {
        "name": "The Box",
        "neighborhood": "Lower East Side",
        "instagram_handle": "theboxnewyork",
        "venue_type": "nightclub",
        "address": "189 Chrystie St, New York, NY 10002",
        "description": "Theatrical nightclub with burlesque performances",
        "busy_nights": "Wed,Thu,Fri,Sat",
        "price_range": "$$$$"
    },
    {
        "name": "Beauty & Essex",
        "neighborhood": "Lower East Side",
        "instagram_handle": "beautyandessex",
        "venue_type": "cocktail_lounge",
        "address": "146 Essex St, New York, NY 10002",
        "description": "Upscale lounge hidden behind a pawn shop",
        "busy_nights": "Thu,Fri,Sat",
        "price_range": "$$$"
    },
    
    # Brooklyn - Williamsburg
    {
        "name": "Brooklyn Bowl",
        "neighborhood": "Williamsburg",
        "instagram_handle": "brooklynbowl",
        "venue_type": "live_music_venue",
        "address": "61 Wythe Ave, Brooklyn, NY 11249",
        "description": "Bowling alley, music venue, and restaurant",
        "busy_nights": "Fri,Sat,Sun",
        "price_range": "$$"
    },
    {
        "name": "Output",
        "neighborhood": "Williamsburg",
        "instagram_handle": "outputclub",
        "venue_type": "dance_club",
        "address": "74 Wythe Ave, Brooklyn, NY 11249",
        "description": "Premier electronic music club with rooftop",
        "busy_nights": "Thu,Fri,Sat",
        "price_range": "$$$"
    },
    {
        "name": "Baby's All Right",
        "neighborhood": "Williamsburg",
        "instagram_handle": "babysallright",
        "venue_type": "live_music_venue",
        "address": "146 Broadway, Brooklyn, NY 11211",
        "description": "Music venue and bar with diverse lineup",
        "busy_nights": "Wed,Thu,Fri,Sat",
        "price_range": "$$"
    },
    
    # Manhattan - East Village
    {
        "name": "Death & Co",
        "neighborhood": "East Village",
        "instagram_handle": "deathandcompany",
        "venue_type": "cocktail_bar",
        "address": "433 E 6th St, New York, NY 10009",
        "description": "Award-winning craft cocktail bar",
        "busy_nights": "Thu,Fri,Sat",
        "price_range": "$$$"
    },
    {
        "name": "PDT (Please Don't Tell)",
        "neighborhood": "East Village",
        "instagram_handle": "pdtnyc",
        "venue_type": "speakeasy",
        "address": "113 St Marks Pl, New York, NY 10009",
        "description": "Hidden speakeasy accessed through phone booth",
        "busy_nights": "Wed,Thu,Fri,Sat",
        "price_range": "$$$"
    },
    
    # Brooklyn - Bushwick
    {
        "name": "House of Yes",
        "neighborhood": "Bushwick",
        "instagram_handle": "houseofyes",
        "venue_type": "nightclub",
        "address": "2 Wyckoff Ave, Brooklyn, NY 11237",
        "description": "Creative nightclub with themed parties and performances",
        "busy_nights": "Wed,Thu,Fri,Sat",
        "price_range": "$$"
    },
    {
        "name": "Elsewhere",
        "neighborhood": "Bushwick",
        "instagram_handle": "elsewherespace",
        "venue_type": "live_music_venue",
        "address": "599 Johnson Ave, Brooklyn, NY 11237",
        "description": "Multi-room music venue and nightclub",
        "busy_nights": "Thu,Fri,Sat",
        "price_range": "$$"
    },
    
    # Manhattan - Chelsea
    {
        "name": "Le Bain",
        "neighborhood": "Chelsea",
        "instagram_handle": "lebainnewyork",
        "venue_type": "rooftop_bar",
        "address": "444 W 13th St, New York, NY 10014",
        "description": "Rooftop disco and bar at The Standard High Line",
        "busy_nights": "Thu,Fri,Sat,Sun",
        "price_range": "$$$"
    },
    {
        "name": "Marquee New York",
        "neighborhood": "Chelsea",
        "instagram_handle": "marqueeny",
        "venue_type": "nightclub",
        "address": "289 10th Ave, New York, NY 10001",
        "description": "Upscale nightclub with world-class DJs",
        "busy_nights": "Wed,Fri,Sat",
        "price_range": "$$$$"
    },
    
    # Manhattan - West Village
    {
        "name": "Employees Only",
        "neighborhood": "West Village",
        "instagram_handle": "employeesonlynyc",
        "venue_type": "cocktail_bar",
        "address": "510 Hudson St, New York, NY 10014",
        "description": "Prohibition-style bar with late-night menu",
        "busy_nights": "Thu,Fri,Sat",
        "price_range": "$$$"
    },
    {
        "name": "The Jane Ballroom",
        "neighborhood": "West Village",
        "instagram_handle": "thejaneballroom",
        "venue_type": "nightclub",
        "address": "113 Jane St, New York, NY 10014",
        "description": "Historic ballroom turned nightclub",
        "busy_nights": "Fri,Sat",
        "price_range": "$$$"
    },
    
    # Queens - Long Island City
    {
        "name": "The Foundry",
        "neighborhood": "Long Island City",
        "instagram_handle": "foundrylicbar",
        "venue_type": "event_space",
        "address": "42-38 9th St, Long Island City, NY 11101",
        "description": "Industrial event space and bar",
        "busy_nights": "Fri,Sat",
        "price_range": "$$"
    },
    
    # Manhattan - Midtown
    {
        "name": "The Press Lounge",
        "neighborhood": "Midtown",
        "instagram_handle": "thepresslounge",
        "venue_type": "rooftop_bar",
        "address": "653 11th Ave, New York, NY 10036",
        "description": "Rooftop bar with panoramic city views",
        "busy_nights": "Thu,Fri,Sat",
        "price_range": "$$$"
    },
    {
        "name": "Jimmy's Corner",
        "neighborhood": "Midtown",
        "instagram_handle": "jimmyscornernyc",
        "venue_type": "dive_bar",
        "address": "140 W 44th St, New York, NY 10036",
        "description": "Classic Times Square dive bar",
        "busy_nights": "Thu,Fri,Sat",
        "price_range": "$"
    },
    
    # Brooklyn - Park Slope
    {
        "name": "Union Hall",
        "neighborhood": "Park Slope",
        "instagram_handle": "unionhallny",
        "venue_type": "bar",
        "address": "702 Union St, Brooklyn, NY 11215",
        "description": "Bar with bocce courts and live music",
        "busy_nights": "Fri,Sat,Sun",
        "price_range": "$$"
    },
    
    # Manhattan - Upper East Side
    {
        "name": "The Penrose",
        "neighborhood": "Upper East Side",
        "instagram_handle": "thepenrosenyc",
        "venue_type": "gastropub",
        "address": "1590 2nd Ave, New York, NY 10028",
        "description": "Upscale gastropub with craft cocktails",
        "busy_nights": "Thu,Fri,Sat",
        "price_range": "$$"
    },
    
    # Brooklyn - Crown Heights
    {
        "name": "Friends and Lovers",
        "neighborhood": "Crown Heights",
        "instagram_handle": "friendsandloversnyc",
        "venue_type": "dance_club",
        "address": "641 Classon Ave, Brooklyn, NY 11238",
        "description": "Underground dance club with diverse music",
        "busy_nights": "Fri,Sat",
        "price_range": "$$"
    }
]

def import_venues():
    """Import venues into the database"""
    db = VenueDatabase()
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY) if settings.GOOGLE_MAPS_API_KEY else None
    
    print(f"🚀 Starting import of {len(NYC_VENUES)} NYC venues...")
    print(f"📍 Google Maps {'enabled' if gmaps else 'disabled'}")
    
    imported = 0
    skipped = 0
    errors = 0
    
    for venue_data in NYC_VENUES:
        try:
            # Check if venue already exists
            existing = db.get_all_venues()
            if any(v.instagram_handle == venue_data['instagram_handle'] for v in existing):
                print(f"⏭️  Skipping {venue_data['name']} - already exists")
                skipped += 1
                continue
            
            # Get coordinates from Google Maps if available
            lat, lng = None, None
            if gmaps and venue_data.get('address'):
                try:
                    geocode_result = gmaps.geocode(venue_data['address'])
                    if geocode_result:
                        location = geocode_result[0]['geometry']['location']
                        lat = location['lat']
                        lng = location['lng']
                        print(f"📍 Found coordinates for {venue_data['name']}: {lat}, {lng}")
                except Exception as e:
                    print(f"⚠️  Could not geocode {venue_data['name']}: {e}")
            
            # Create venue
            venue = Venue(
                name=venue_data['name'],
                neighborhood=venue_data['neighborhood'],
                instagram_handle=venue_data['instagram_handle'],
                venue_type=venue_data['venue_type'],
                address=venue_data.get('address'),
                description=venue_data.get('description'),
                busy_nights=venue_data.get('busy_nights'),
                price_range=venue_data.get('price_range')
            )
            
            # Add to database
            venue_id = db.add_venue(venue)
            if venue_id > 0:
                print(f"✅ Imported {venue_data['name']} (ID: {venue_id})")
                imported += 1
                
                # Add coordinates if available
                if lat and lng:
                    # You could extend the database to store coordinates
                    pass
            else:
                print(f"❌ Failed to import {venue_data['name']}")
                errors += 1
            
            # Rate limit for Google Maps API
            if gmaps:
                time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Error importing {venue_data['name']}: {e}")
            errors += 1
    
    print(f"\n📊 Import Summary:")
    print(f"✅ Imported: {imported}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")
    print(f"📊 Total venues in database: {len(db.get_all_venues())}")

def export_sample_data():
    """Export sample venue data for reference"""
    db = VenueDatabase()
    venues = db.get_all_venues()
    
    if venues:
        print(f"\n📝 Current venues in database:")
        for v in venues[:10]:  # Show first 10
            print(f"- {v.name} (@{v.instagram_handle}) - {v.neighborhood}")
        
        if len(venues) > 10:
            print(f"... and {len(venues) - 10} more")

if __name__ == "__main__":
    print("🌆 Atlas-NYC Venue Importer")
    print("=" * 50)
    
    # Import venues
    import_venues()
    
    # Show current data
    export_sample_data()
    
    print("\n✨ Done! Your NYC nightlife database is ready.")
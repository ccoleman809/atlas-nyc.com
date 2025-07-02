#!/usr/bin/env python3
"""
Simple script to add venues directly to the database
"""

import sqlite3

# Connect to the database
conn = sqlite3.connect('nightlife.db')
cursor = conn.cursor()

# Count current venues
cursor.execute("SELECT COUNT(*) FROM venues")
before_count = cursor.fetchone()[0]
print(f"Venues before: {before_count}")

# Essential venues to add
essential_venues = [
    ("Death & Co", "East Village", "deathandcompany", "cocktail_bar", "433 E 6th St", "Award-winning cocktail bar", "Thu,Fri,Sat", "$$$"),
    ("Please Don't Tell", "East Village", "pdtnyc", "cocktail_bar", "113 St Marks Pl", "Speakeasy in phone booth", "Fri,Sat", "$$$"),
    ("The Box", "Lower East Side", "theboxnyc", "nightclub", "189 Chrystie St", "Burlesque and variety shows", "Thu,Fri,Sat", "$$$$"),
    ("Mr. Purple", "Lower East Side", "mrpurplenyc", "rooftop_bar", "180 Orchard St", "Rooftop bar with city views", "Fri,Sat,Sun", "$$$"),
    ("Employees Only", "West Village", "employeesonlynyc", "cocktail_bar", "510 Hudson St", "Prohibition-style cocktail bar", "Thu,Fri,Sat", "$$$"),
    ("The Django", "West Village", "thedjangonyc", "live_music_venue", "2 6th Ave", "Jazz club and cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
    ("Le Bain", "Meatpacking", "lebainnewyork", "rooftop_bar", "848 Washington St", "Rooftop disco with pool", "Thu,Fri,Sat", "$$$$"),
    ("Gallow Green", "Chelsea", "gallowgreen", "rooftop_bar", "542 W 27th St", "Rooftop garden bar", "Wed,Thu,Fri,Sat", "$$$"),
    ("Rainbow Room", "Midtown", "rainbowroomnyc", "lounge", "30 Rockefeller Plaza", "Iconic supper club", "Fri,Sat", "$$$$"),
    ("Birdland", "Midtown", "birdlandjazz", "live_music_venue", "315 W 44th St", "Historic jazz club", "Daily", "$$$"),
    ("Bemelmans Bar", "Upper East Side", "bemelmansbar", "cocktail_bar", "35 E 76th St", "Classic piano bar", "Tue,Wed,Thu,Fri,Sat", "$$$$"),
    ("Brooklyn Bowl", "Williamsburg", "brooklynbowl", "live_music_venue", "61 Wythe Ave", "Bowling and music venue", "Thu,Fri,Sat", "$$"),
    ("Output", "Williamsburg", "outputclub", "nightclub", "74 Wythe Ave", "Underground dance club", "Fri,Sat", "$$$"),
    ("The Ides", "Williamsburg", "theidesbar", "rooftop_bar", "80 Wythe Ave", "Wythe Hotel rooftop", "Thu,Fri,Sat,Sun", "$$$"),
    ("House of Yes", "Bushwick", "houseofyes", "nightclub", "2 Wyckoff Ave", "Creative themed parties", "Thu,Fri,Sat", "$$"),
    ("Mood Ring", "Bushwick", "moodringbar", "bar", "1260 Myrtle Ave", "Astrology-themed bar", "Wed,Thu,Fri,Sat", "$$"),
    ("Union Hall", "Park Slope", "unionhallny", "bar", "702 Union St", "Bar with bocce courts", "Thu,Fri,Sat", "$$"),
    ("Dutch Kills", "Long Island City", "dutchkillsbar", "cocktail_bar", "27-24 Jackson Ave", "Craft cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
    ("Blue Note", "West Village", "bluenotenyc", "culture", "131 W 3rd St", "Legendary jazz club", "Daily", "$$$"),
    ("Comedy Cellar", "West Village", "comedycellar", "culture", "117 MacDougal St", "Famous comedy club", "Daily", "$$"),
]

# Insert venues
added = 0
for venue in essential_venues:
    try:
        cursor.execute("""
            INSERT INTO venues (name, neighborhood, instagram_handle, venue_type, address, description, busy_nights, price_range)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, venue)
        added += 1
        print(f"✅ Added: {venue[0]}")
    except sqlite3.IntegrityError:
        print(f"⏭️  Exists: {venue[0]}")

# Commit and check final count
conn.commit()
cursor.execute("SELECT COUNT(*) FROM venues")
after_count = cursor.fetchone()[0]

print(f"\nAdded {added} new venues")
print(f"Total venues: {after_count} (was {before_count})")

# Show neighborhood distribution
cursor.execute("SELECT neighborhood, COUNT(*) FROM venues GROUP BY neighborhood ORDER BY COUNT(*) DESC")
neighborhoods = cursor.fetchall()
print(f"\nVenues by neighborhood:")
for neighborhood, count in neighborhoods:
    print(f"  {neighborhood}: {count}")

conn.close()
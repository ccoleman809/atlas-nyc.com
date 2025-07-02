import sqlite3
import os

# Connect to database
db_path = "nightlife.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List of venues to add (name, neighborhood, instagram_handle, venue_type, address, description, busy_nights, price_range)
venues_to_add = [
    ("Death & Co", "East Village", "deathandcompany", "cocktail_bar", "433 E 6th St", "Award-winning cocktail bar", "Thu,Fri,Sat", "$$$"),
    ("Please Don't Tell", "East Village", "pdtnyc", "cocktail_bar", "113 St Marks Pl", "Speakeasy accessed through phone booth", "Fri,Sat", "$$$"),
    ("The Wayland", "East Village", "thewaylandnyc", "bar", "700 E 9th St", "Craft cocktails and live music", "Wed,Thu,Fri,Sat", "$$"),
    ("Angel's Share", "East Village", "angelsharenyc", "cocktail_bar", "8 Stuyvesant St", "Hidden Japanese cocktail bar", "Thu,Fri,Sat", "$$$"),
    ("The Box", "Lower East Side", "theboxnyc", "nightclub", "189 Chrystie St", "Burlesque and variety shows", "Thu,Fri,Sat", "$$$$"),
    ("Pianos", "Lower East Side", "pianosnyc", "live_music_venue", "158 Ludlow St", "Live music venue and bar", "Thu,Fri,Sat", "$$"),
    ("Mr. Purple", "Lower East Side", "mrpurplenyc", "rooftop_bar", "180 Orchard St", "Rooftop bar with city views", "Fri,Sat,Sun", "$$$"),
    ("Attaboy", "Lower East Side", "attaboy_ny", "cocktail_bar", "134 Eldridge St", "No-menu craft cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
    ("Employees Only", "West Village", "employeesonlynyc", "cocktail_bar", "510 Hudson St", "Prohibition-style cocktail bar", "Thu,Fri,Sat", "$$$"),
    ("Little Branch", "West Village", "littlebranchnyc", "cocktail_bar", "20 7th Ave S", "Jazz and cocktails in basement bar", "Mon,Tue,Wed,Thu,Fri,Sat", "$$"),
    ("Henrietta Hudson", "West Village", "henriettahudson", "bar", "438 Hudson St", "Lesbian bar and dance club", "Thu,Fri,Sat", "$$"),
    ("The Django", "West Village", "thedjangonyc", "live_music_venue", "2 6th Ave", "Jazz club and cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
    ("The High Line Hotel Bar", "Chelsea", "highlinehotel", "bar", "180 10th Ave", "Refectory bar in former seminary", "Thu,Fri,Sat", "$$$"),
    ("Rebar", "Chelsea", "rebarchelsea", "bar", "225 W 19th St", "Gay sports bar", "Thu,Fri,Sat", "$$"),
    ("Gallow Green", "Chelsea", "gallowgreen", "rooftop_bar", "542 W 27th St", "Rooftop garden bar at McKittrick Hotel", "Wed,Thu,Fri,Sat", "$$$"),
    ("Le Bain", "Meatpacking", "lebainnewyork", "rooftop_bar", "848 Washington St", "Rooftop disco and bar with pool", "Thu,Fri,Sat", "$$$$"),
    ("PhD Rooftop", "Meatpacking", "phdrooftop", "rooftop_bar", "355 W 16th St", "Rooftop lounge at Dream Downtown", "Thu,Fri,Sat", "$$$"),
    ("Brass Monkey", "Meatpacking", "brassmonkeynyc", "bar", "55 Little W 12th St", "Multi-level bar with roof deck", "Fri,Sat", "$$"),
    ("Paul's Casablanca", "SoHo", "paulscasablanca", "cocktail_bar", "305 Spring St", "New Orleans-inspired cocktail bar", "Thu,Fri,Sat", "$$"),
    ("Pegu Club", "SoHo", "peguclubnyc", "cocktail_bar", "77 W Houston St", "Classic cocktail destination", "Wed,Thu,Fri,Sat", "$$$"),
    ("Temple Bar", "SoHo", "templebarmanhattan", "cocktail_bar", "332 Lafayette St", "Upscale cocktail lounge", "Thu,Fri,Sat", "$$$"),
    ("Ward III", "Tribeca", "wardiii", "cocktail_bar", "111 Reade St", "Neighborhood cocktail bar", "Thu,Fri,Sat", "$$"),
    ("Weather Up", "Tribeca", "weatheruptribeca", "cocktail_bar", "159 Duane St", "Intimate cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
    ("Press Lounge", "Midtown", "presslounge", "rooftop_bar", "653 11th Ave", "Rooftop bar with Hudson views", "Thu,Fri,Sat", "$$$"),
    ("The Campbell", "Midtown", "thecampbellnyc", "cocktail_bar", "15 Vanderbilt Ave", "Historic bar in Grand Central", "Wed,Thu,Fri", "$$$"),
    ("Rainbow Room", "Midtown", "rainbowroomnyc", "lounge", "30 Rockefeller Plaza", "Iconic supper club with views", "Fri,Sat", "$$$$"),
    ("Birdland", "Midtown", "birdlandjazz", "live_music_venue", "315 W 44th St", "Historic jazz club", "Mon,Tue,Wed,Thu,Fri,Sat,Sun", "$$$"),
    ("The Penrose", "Upper East Side", "thepenrosenyc", "bar", "1590 2nd Ave", "Cork-lined gastropub", "Thu,Fri,Sat", "$$"),
    ("Bemelmans Bar", "Upper East Side", "bemelmansbar", "cocktail_bar", "35 E 76th St", "Classic piano bar at The Carlyle", "Tue,Wed,Thu,Fri,Sat", "$$$$"),
    ("Seamstress", "Upper East Side", "seamstressny", "cocktail_bar", "339 E 75th St", "Cocktail bar with secret back room", "Thu,Fri,Sat", "$$$"),
    ("Brooklyn Bowl", "Williamsburg", "brooklynbowl", "live_music_venue", "61 Wythe Ave", "Bowling, music venue, and restaurant", "Thu,Fri,Sat", "$$"),
    ("Output", "Williamsburg", "outputclub", "nightclub", "74 Wythe Ave", "Underground dance club", "Fri,Sat", "$$$"),
    ("Union Pool", "Williamsburg", "unionpool", "bar", "484 Union Ave", "Bar with taco truck and fire pit", "Thu,Fri,Sat", "$$"),
    ("Baby's All Right", "Williamsburg", "babysallright", "live_music_venue", "146 Broadway", "Music venue and restaurant", "Wed,Thu,Fri,Sat", "$$"),
    ("The Ides", "Williamsburg", "theidesbar", "rooftop_bar", "80 Wythe Ave", "Rooftop bar at Wythe Hotel", "Thu,Fri,Sat,Sun", "$$$"),
    ("Westlight", "Williamsburg", "westlightnyc", "rooftop_bar", "111 N 12th St", "22nd floor rooftop bar", "Wed,Thu,Fri,Sat", "$$$"),
    ("House of Yes", "Bushwick", "houseofyes", "nightclub", "2 Wyckoff Ave", "Creative nightclub with themed parties", "Thu,Fri,Sat", "$$"),
    ("Mood Ring", "Bushwick", "moodringbar", "bar", "1260 Myrtle Ave", "Astrology-themed bar", "Wed,Thu,Fri,Sat", "$$"),
    ("The Keep", "Bushwick", "thekeepny", "bar", "205 Cypress Ave", "Board game bar", "Thu,Fri,Sat", "$$"),
    ("Bossa Nova Civic Club", "Bushwick", "bossanovacivicclub", "nightclub", "1271 Myrtle Ave", "Underground dance club", "Fri,Sat", "$$"),
    ("Union Hall", "Park Slope", "unionhallny", "bar", "702 Union St", "Bar with bocce courts", "Thu,Fri,Sat", "$$"),
    ("Barbès", "Park Slope", "barbesbrooklyn", "live_music_venue", "376 9th St", "World music venue", "Tue,Wed,Thu,Fri,Sat,Sun", "$"),
    ("Butter & Scotch", "Crown Heights", "butterandscotch", "bar", "818 Franklin Ave", "Dessert bar with cocktails", "Thu,Fri,Sat", "$$"),
    ("Friends and Lovers", "Crown Heights", "friendsandlovers", "nightclub", "641 Classon Ave", "Dance club and music venue", "Fri,Sat", "$$"),
    ("Dutch Kills", "Long Island City", "dutchkillsbar", "cocktail_bar", "27-24 Jackson Ave", "Craft cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
    ("LIC Bar", "Long Island City", "licbar", "dive_bar", "45-58 Vernon Blvd", "Dive bar with outdoor space", "Thu,Fri,Sat", "$"),
    ("Bushwig", "Brooklyn", "bushwig", "events", "Various Locations", "Annual drag festival", "September", "$$"),
    ("Brooklyn Mirage", "Brooklyn", "brooklynmirage", "events", "140 Stewart Ave", "Outdoor electronic music venue", "Fri,Sat,Sun", "$$$"),
    ("House of X", "Manhattan", "houseofx", "events", "Various Locations", "Queer party collective", "Monthly", "$$"),
    ("Sleep No More", "Chelsea", "sleepnomorenyc", "culture", "530 W 27th St", "Immersive theater experience", "Wed,Thu,Fri,Sat,Sun", "$$$$"),
    ("Blue Note", "West Village", "bluenotenyc", "culture", "131 W 3rd St", "Legendary jazz club", "Mon,Tue,Wed,Thu,Fri,Sat,Sun", "$$$"),
    ("Comedy Cellar", "West Village", "comedycellar", "culture", "117 MacDougal St", "Famous comedy club", "Mon,Tue,Wed,Thu,Fri,Sat,Sun", "$$"),
]

# Check current count
cursor.execute("SELECT COUNT(*) FROM venues")
initial_count = cursor.fetchone()[0]
print(f"Starting with {initial_count} venues")

# Add venues
added = 0
skipped = 0

for venue_data in venues_to_add:
    try:
        cursor.execute("""
            INSERT INTO venues (name, neighborhood, instagram_handle, venue_type, address, description, busy_nights, price_range)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, venue_data)
        print(f"✅ Added: {venue_data[0]} ({venue_data[1]})")
        added += 1
    except sqlite3.IntegrityError:
        print(f"⏭️  Skipped: {venue_data[0]} (already exists)")
        skipped += 1

# Commit changes
conn.commit()

# Final count
cursor.execute("SELECT COUNT(*) FROM venues")
final_count = cursor.fetchone()[0]

print(f"\n📊 Summary:")
print(f"   Started with: {initial_count} venues")
print(f"   Added: {added} new venues")
print(f"   Skipped: {skipped} duplicates")
print(f"   Total now: {final_count} venues")

# Show distribution by neighborhood
cursor.execute("SELECT neighborhood, COUNT(*) FROM venues GROUP BY neighborhood ORDER BY neighborhood")
neighborhoods = cursor.fetchall()

print(f"\n📍 Venues by neighborhood:")
for neighborhood, count in neighborhoods:
    print(f"   {neighborhood}: {count}")

# Show distribution by type
cursor.execute("SELECT venue_type, COUNT(*) FROM venues GROUP BY venue_type ORDER BY venue_type")
types = cursor.fetchall()

print(f"\n🎭 Venues by type:")
for venue_type, count in types:
    print(f"   {venue_type}: {count}")

conn.close()
print(f"\n✨ Database updated successfully!")
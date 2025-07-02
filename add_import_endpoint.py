#!/usr/bin/env python3
"""
Add a temporary endpoint to production_api.py for importing venues
"""

# Read the current production_api.py
with open('production_api.py', 'r') as f:
    content = f.read()

# Find where to insert the new endpoint (after the /venues DELETE endpoint)
insert_position = content.find('@app.delete("/venues/{venue_id}")')
if insert_position == -1:
    print("Could not find insertion point!")
    exit(1)

# Find the end of the delete endpoint function
search_from = insert_position
endpoint_end = content.find('\n@app.', search_from)
if endpoint_end == -1:
    endpoint_end = content.find('\nif __name__', search_from)

# Create the import endpoint code
import_endpoint = '''
@app.post("/admin/import-venues")
async def import_all_venues(admin_user: str = Depends(verify_admin)):
    """Import all NYC venues - TEMPORARY ENDPOINT"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # All venues to import
    all_venues = [
        # Manhattan - East Village
        ("Death & Co", "East Village", "deathandcompany", "cocktail_bar", "433 E 6th St", "Award-winning cocktail bar", "Thu,Fri,Sat", "$$$"),
        ("Please Don't Tell", "East Village", "pdtnyc", "cocktail_bar", "113 St Marks Pl", "Speakeasy accessed through phone booth", "Fri,Sat", "$$$"),
        ("The Wayland", "East Village", "thewaylandnyc", "bar", "700 E 9th St", "Craft cocktails and live music", "Wed,Thu,Fri,Sat", "$$"),
        ("Angel's Share", "East Village", "angelsharenyc", "cocktail_bar", "8 Stuyvesant St", "Hidden Japanese cocktail bar", "Thu,Fri,Sat", "$$$"),
        
        # Manhattan - Lower East Side
        ("The Box", "Lower East Side", "theboxnyc", "nightclub", "189 Chrystie St", "Burlesque and variety shows", "Thu,Fri,Sat", "$$$$"),
        ("Pianos", "Lower East Side", "pianosnyc", "live_music_venue", "158 Ludlow St", "Live music venue and bar", "Thu,Fri,Sat", "$$"),
        ("Mr. Purple", "Lower East Side", "mrpurplenyc", "rooftop_bar", "180 Orchard St", "Rooftop bar with city views", "Fri,Sat,Sun", "$$$"),
        ("Attaboy", "Lower East Side", "attaboy_ny", "cocktail_bar", "134 Eldridge St", "No-menu craft cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
        
        # Manhattan - West Village
        ("Employees Only", "West Village", "employeesonlynyc", "cocktail_bar", "510 Hudson St", "Prohibition-style cocktail bar", "Thu,Fri,Sat", "$$$"),
        ("Little Branch", "West Village", "littlebranchnyc", "cocktail_bar", "20 7th Ave S", "Jazz and cocktails in basement bar", "Mon,Tue,Wed,Thu,Fri,Sat", "$$"),
        ("Henrietta Hudson", "West Village", "henriettahudson", "bar", "438 Hudson St", "Lesbian bar and dance club", "Thu,Fri,Sat", "$$"),
        ("The Django", "West Village", "thedjangonyc", "live_music_venue", "2 6th Ave", "Jazz club and cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("Blue Note", "West Village", "bluenotenyc", "culture", "131 W 3rd St", "Legendary jazz club", "Daily", "$$$"),
        ("Comedy Cellar", "West Village", "comedycellar", "culture", "117 MacDougal St", "Famous comedy club", "Daily", "$$"),
        
        # Manhattan - Chelsea
        ("Gallow Green", "Chelsea", "gallowgreen", "rooftop_bar", "542 W 27th St", "Rooftop garden bar at McKittrick Hotel", "Wed,Thu,Fri,Sat", "$$$"),
        ("Sleep No More", "Chelsea", "sleepnomorenyc", "culture", "530 W 27th St", "Immersive theater experience", "Wed,Thu,Fri,Sat,Sun", "$$$$"),
        
        # Manhattan - Meatpacking
        ("Le Bain", "Meatpacking", "lebainnewyork", "rooftop_bar", "848 Washington St", "Rooftop disco and bar with pool", "Thu,Fri,Sat", "$$$$"),
        ("PhD Rooftop", "Meatpacking", "phdrooftop", "rooftop_bar", "355 W 16th St", "Rooftop lounge at Dream Downtown", "Thu,Fri,Sat", "$$$"),
        
        # Manhattan - Midtown
        ("Press Lounge", "Midtown", "presslounge", "rooftop_bar", "653 11th Ave", "Rooftop bar with Hudson views", "Thu,Fri,Sat", "$$$"),
        ("Rainbow Room", "Midtown", "rainbowroomnyc", "lounge", "30 Rockefeller Plaza", "Iconic supper club with views", "Fri,Sat", "$$$$"),
        ("Birdland", "Midtown", "birdlandjazz", "live_music_venue", "315 W 44th St", "Historic jazz club", "Mon,Tue,Wed,Thu,Fri,Sat,Sun", "$$$"),
        
        # Manhattan - Upper East Side
        ("Bemelmans Bar", "Upper East Side", "bemelmansbar", "cocktail_bar", "35 E 76th St", "Classic piano bar at The Carlyle", "Tue,Wed,Thu,Fri,Sat", "$$$$"),
        
        # Brooklyn - Williamsburg
        ("Brooklyn Bowl", "Williamsburg", "brooklynbowl", "live_music_venue", "61 Wythe Ave", "Bowling, music venue, and restaurant", "Thu,Fri,Sat", "$$"),
        ("Output", "Williamsburg", "outputclub", "nightclub", "74 Wythe Ave", "Underground dance club", "Fri,Sat", "$$$"),
        ("Union Pool", "Williamsburg", "unionpool", "bar", "484 Union Ave", "Bar with taco truck and fire pit", "Thu,Fri,Sat", "$$"),
        ("Baby's All Right", "Williamsburg", "babysallright", "live_music_venue", "146 Broadway", "Music venue and restaurant", "Wed,Thu,Fri,Sat", "$$"),
        ("The Ides", "Williamsburg", "theidesbar", "rooftop_bar", "80 Wythe Ave", "Rooftop bar at Wythe Hotel", "Thu,Fri,Sat,Sun", "$$$"),
        ("Westlight", "Williamsburg", "westlightnyc", "rooftop_bar", "111 N 12th St", "22nd floor rooftop bar", "Wed,Thu,Fri,Sat", "$$$"),
        
        # Brooklyn - Bushwick
        ("House of Yes", "Bushwick", "houseofyes", "nightclub", "2 Wyckoff Ave", "Creative nightclub with themed parties", "Thu,Fri,Sat", "$$"),
        ("Mood Ring", "Bushwick", "moodringbar", "bar", "1260 Myrtle Ave", "Astrology-themed bar", "Wed,Thu,Fri,Sat", "$$"),
        
        # Queens - Long Island City
        ("Dutch Kills", "Long Island City", "dutchkillsbar", "cocktail_bar", "27-24 Jackson Ave", "Craft cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
    ]
    
    added = 0
    skipped = 0
    
    for venue_data in all_venues:
        try:
            venue = Venue(
                name=venue_data[0],
                neighborhood=venue_data[1],
                instagram_handle=venue_data[2],
                venue_type=venue_data[3],
                address=venue_data[4],
                description=venue_data[5],
                busy_nights=venue_data[6],
                price_range=venue_data[7]
            )
            result = db.add_venue(venue)
            if result > 0:
                added += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Error adding {venue_data[0]}: {e}")
            skipped += 1
    
    # Clear cache
    _get_cached_venues.cache_clear()
    
    return {
        "success": True,
        "message": f"Import complete! Added {added} venues, skipped {skipped} duplicates.",
        "total_added": added,
        "total_skipped": skipped
    }

'''

# Insert the new endpoint
new_content = content[:endpoint_end] + '\n' + import_endpoint + content[endpoint_end:]

# Write the updated file
with open('production_api.py', 'w') as f:
    f.write(new_content)

print("✅ Import endpoint added to production_api.py")
print("📌 After deployment, you can trigger import at: POST /admin/import-venues")
print("🔐 Remember: This requires admin authentication!")
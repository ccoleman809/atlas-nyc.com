#!/usr/bin/env python3
"""
Production-ready Atlas-NYC API with database connection
"""

from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os
from datetime import datetime
from venue_db import VenueDatabase, Venue
from pathlib import Path
from typing import Optional

# Create FastAPI app
app = FastAPI(title="Atlas-NYC API", version="2.0.0")

# Security
security = HTTPBasic()

# Admin credentials
ADMIN_USERNAME = "doughboy809"
ADMIN_PASSWORD = "Allstate@168"

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
try:
    db = VenueDatabase()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"⚠️ Database initialization failed: {e}")
    db = None

# Authentication function
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials"""
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Atlas-NYC API is running!",
        "version": "2.0.0",
        "status": "production",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if db else "not_connected"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if db else "not_connected",
        "environment": os.environ.get("ENVIRONMENT", "production")
    }

@app.get("/venues")
async def get_venues(
    page: int = 1,
    per_page: int = 20,
    neighborhood: str = None,
    venue_type: str = None
):
    """Get venues from database with pagination"""
    try:
        if not db:
            # Return sample data if database not available
            return {
                "venues": [
                    {
                        "id": 1,
                        "name": "House of Yes",
                        "neighborhood": "Bushwick",
                        "instagram_handle": "houseofyes",
                        "venue_type": "nightclub",
                        "description": "Creative nightclub with themed parties",
                        "lat": 40.7053,
                        "lng": -73.9233
                    },
                    {
                        "id": 2,
                        "name": "Brooklyn Bowl",
                        "neighborhood": "Williamsburg",
                        "instagram_handle": "brooklynbowl",
                        "venue_type": "live_music_venue",
                        "description": "Bowling alley, music venue, and restaurant",
                        "lat": 40.7220,
                        "lng": -73.9575
                    }
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 2,
                    "pages": 1
                },
                "source": "sample_data"
            }
        
        # Get all venues from database
        all_venues = db.get_all_venues()
        
        # Apply filters
        filtered_venues = all_venues
        if neighborhood:
            filtered_venues = [v for v in filtered_venues if v.neighborhood.lower() == neighborhood.lower()]
        if venue_type:
            filtered_venues = [v for v in filtered_venues if v.venue_type == venue_type]
        
        # Calculate pagination
        total = len(filtered_venues)
        start = (page - 1) * per_page
        end = start + per_page
        
        # Get page of venues
        page_venues = filtered_venues[start:end]
        
        # Format response
        venues_data = []
        for v in page_venues:
            venue_dict = {
                "id": v.venue_id,
                "name": v.name,
                "neighborhood": v.neighborhood,
                "instagram_handle": v.instagram_handle,
                "venue_type": v.venue_type,
                "description": v.description,
                "busy_nights": v.busy_nights,
                "price_range": v.price_range
            }
            
            # Add coordinates based on venue and neighborhood
            # Create consistent coordinates by using venue name hash for offset
            import hashlib
            
            neighborhood_coords = {
                "Bushwick": {"lat": 40.6942, "lng": -73.9249},
                "Williamsburg": {"lat": 40.7081, "lng": -73.9571},
                "East Village": {"lat": 40.7264, "lng": -73.9818},
                "Lower East Side": {"lat": 40.7209, "lng": -73.9896},
                "West Village": {"lat": 40.7335, "lng": -74.0027},
                "Chelsea": {"lat": 40.7465, "lng": -73.9972},
                "Meatpacking": {"lat": 40.7411, "lng": -74.0078},
                "SoHo": {"lat": 40.7230, "lng": -74.0020},
                "Tribeca": {"lat": 40.7195, "lng": -74.0089},
                "Midtown": {"lat": 40.7505, "lng": -73.9934},
                "Upper East Side": {"lat": 40.7736, "lng": -73.9566},
                "Upper West Side": {"lat": 40.7870, "lng": -73.9754},
                "Park Slope": {"lat": 40.6736, "lng": -73.9780},
                "Crown Heights": {"lat": 40.6677, "lng": -73.9442},
                "Long Island City": {"lat": 40.7505, "lng": -73.9370},
                "Brooklyn": {"lat": 40.6782, "lng": -73.9442},
                "Queens": {"lat": 40.7282, "lng": -73.7949},
                "Bronx": {"lat": 40.8448, "lng": -73.8648},
                "Harlem": {"lat": 40.8116, "lng": -73.9465}
            }
            
            # Get coordinates for the venue's neighborhood
            coords = neighborhood_coords.get(v.neighborhood, {"lat": 40.7589, "lng": -73.9851})
            
            # Create consistent offset using venue name hash (so same venue always gets same coordinates)
            venue_hash = hashlib.md5(v.name.encode()).hexdigest()
            lat_offset = (int(venue_hash[:4], 16) / 65535.0 - 0.5) * 0.006  # ~600m radius
            lng_offset = (int(venue_hash[4:8], 16) / 65535.0 - 0.5) * 0.006
            
            venue_dict.update({
                "lat": round(coords["lat"] + lat_offset, 6),
                "lng": round(coords["lng"] + lng_offset, 6)
            })
            
            venues_data.append(venue_dict)
        
        return {
            "venues": venues_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page if per_page > 0 else 0
            },
            "source": "database"
        }
        
    except Exception as e:
        print(f"Error getting venues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/atlas", response_class=HTMLResponse)
async def get_atlas_interface():
    """Serve the Atlas public interface"""
    try:
        with open("atlas_public_interface.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Atlas interface not found")

@app.get("/admin", response_class=HTMLResponse)
async def get_admin_portal():
    """Serve the admin interface for managing venues"""
    try:
        with open("admin_interface.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Fallback to mobile portal if admin interface not found
        try:
            with open("mobile_portal.html", "r") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Admin portal not found")

@app.post("/venues")
async def create_venue(
    name: str = Form(...),
    neighborhood: str = Form(...),
    instagram_handle: str = Form(...),
    venue_type: str = Form(...),
    address: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    busy_nights: Optional[str] = Form(None),
    price_range: Optional[str] = Form(None),
    admin_user: str = Depends(verify_admin)
):
    """Create a new venue"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Clean instagram handle
        instagram_handle = instagram_handle.strip().replace('@', '')
        
        # Create venue object
        venue = Venue(
            name=name.strip(),
            neighborhood=neighborhood.strip(),
            instagram_handle=instagram_handle,
            venue_type=venue_type.strip(),
            address=address.strip() if address else None,
            description=description.strip() if description else None,
            busy_nights=busy_nights.strip() if busy_nights else None,
            price_range=price_range.strip() if price_range else None
        )
        
        # Add to database
        venue_id = db.add_venue(venue)
        
        if venue_id > 0:
            # Clear cache to show new venue (disabled for now)
            # _get_cached_venues.cache_clear()
            
            return {
                "success": True,
                "message": f"Venue '{name}' added successfully!",
                "id": venue_id
            }
        else:
            raise HTTPException(status_code=400, detail="Venue with this Instagram handle already exists")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating venue: {str(e)}")

@app.put("/venues/{venue_id}")
async def update_venue(
    venue_id: int,
    name: str = Form(...),
    neighborhood: str = Form(...),
    instagram_handle: str = Form(...),
    venue_type: str = Form(...),
    address: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    busy_nights: Optional[str] = Form(None),
    price_range: Optional[str] = Form(None),
    admin_user: str = Depends(verify_admin)
):
    """Update an existing venue"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Check if venue exists
        venues = db.get_all_venues()
        venue_exists = any(v.venue_id == venue_id for v in venues)
        if not venue_exists:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        # Clean instagram handle
        instagram_handle = instagram_handle.strip().replace('@', '')
        
        # Update venue in database
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE venues 
            SET name = ?, neighborhood = ?, instagram_handle = ?, 
                venue_type = ?, address = ?, description = ?, 
                busy_nights = ?, price_range = ?
            WHERE id = ?
        """, (
            name.strip(),
            neighborhood.strip(),
            instagram_handle,
            venue_type.strip(),
            address.strip() if address else None,
            description.strip() if description else None,
            busy_nights.strip() if busy_nights else None,
            price_range.strip() if price_range else None,
            venue_id
        ))
        
        conn.commit()
        conn.close()
        
        # Clear cache to show updated venue (disabled for now)
        # _get_cached_venues.cache_clear()
        
        return {
            "success": True,
            "message": f"Venue '{name}' updated successfully!",
            "id": venue_id
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating venue: {str(e)}")

@app.delete("/venues/{venue_id}")
async def delete_venue(venue_id: int, admin_user: str = Depends(verify_admin)):
    """Delete a venue"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Check if venue exists
        venues = db.get_all_venues()
        venue = next((v for v in venues if v.venue_id == venue_id), None)
        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        # Delete venue from database
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM venues WHERE id = ?", (venue_id,))
        
        conn.commit()
        conn.close()
        
        # Clear cache if it exists
        # _get_cached_venues.cache_clear()
        
        return {
            "success": True,
            "message": f"Venue '{venue.name}' deleted successfully!"
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting venue: {str(e)}")

@app.post("/admin/import-venues")
async def import_all_venues(admin_user: str = Depends(verify_admin)):
    """One-time import of all NYC venues"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    venues_to_add = [
        # Original Brooklyn/Queens venues from your database
        ("Nowadays", "Queens", "nowadaysnyc", "nightclub", "56-06 Cooper Ave", "Outdoor dance venue", "Fri,Sat,Sun", "$$"),
        ("The Keep", "Queens", "thekeepny", "bar", "205 Cypress Ave", "Gaming bar with vintage arcade", "Thu,Fri,Sat", "$$"),
        ("Jupiter Disco", "Bushwick", "jupiterdisco", "nightclub", None, "Underground dance club", "Fri,Sat", "$$"),
        ("Good Room", "Brooklyn", "goodroombk", "nightclub", None, "Dance club with great sound system", "Fri,Sat", "$$$"),
        ("Paragon", "Brooklyn", "paragonbk", "nightclub", None, "Techno and house music venue", "Fri,Sat", "$$"),
        ("Bossa Nova Civic Club", "Bushwick", "bossanovacivicclub", "nightclub", "1271 Myrtle Ave", "Underground dance spot", "Fri,Sat", "$$"),
        ("Market Hotel", "Bushwick", "markethotel", "live_music_venue", None, "DIY music venue", "Thu,Fri,Sat", "$$"),
        ("Trans-Pecos", "Queens", "transpecos", "live_music_venue", None, "Experimental music venue", "Thu,Fri,Sat", "$"),
        ("The Johnsons", "Bushwick", "thejohnsonsnyc", "dive_bar", None, "No-frills dive bar", "Daily", "$"),
        ("Alphaville", "Bushwick", "alphavillenyc", "bar", None, "Video bar and venue", "Wed,Thu,Fri,Sat", "$"),
        ("Lovers Rock", "Brooklyn", "loversrocknyc", "bar", None, "Reggae and rum bar", "Thu,Fri,Sat", "$$"),
        ("Friends and Lovers", "Crown Heights", "friendsandlovers", "nightclub", "641 Classon Ave", "Hip-hop and dance venue", "Fri,Sat", "$$"),
        ("C'mon Everybody", "Brooklyn", "cmoneverybody", "live_music_venue", None, "Music venue and bar", "Wed,Thu,Fri,Sat", "$$"),
        ("The Sultan Room", "Bushwick", "thesultanroom", "live_music_venue", None, "Music venue with rooftop", "Thu,Fri,Sat", "$$"),
        ("Elsewhere", "Bushwick", "elsewherespace", "nightclub", "599 Johnson Ave", "Multi-room music venue", "Thu,Fri,Sat", "$$$"),
        ("Avant Gardner", "Brooklyn", "avantgardner", "nightclub", "140 Stewart Ave", "Large electronic music complex", "Fri,Sat", "$$$"),
        ("Brooklyn Mirage", "Brooklyn", "brooklynmirage", "events", "140 Stewart Ave", "Outdoor electronic music venue", "Fri,Sat,Sun", "$$$"),
        ("Public Records", "Brooklyn", "publicrecords", "nightclub", None, "Hi-fi listening bar and venue", "Thu,Fri,Sat", "$$"),
        ("Music Hall of Williamsburg", "Williamsburg", "musichallofwilliamsburg", "live_music_venue", None, "Popular concert venue", "Varies", "$$"),
        ("Union Pool", "Williamsburg", "unionpool", "bar", "484 Union Ave", "Bar with taco truck", "Thu,Fri,Sat", "$$"),
        ("Schimanski", "Williamsburg", "schimanski", "nightclub", None, "Electronic music venue", "Fri,Sat", "$$$"),
        ("Black Flamingo", "Williamsburg", "blackflamingobk", "nightclub", None, "Plant-based club", "Fri,Sat", "$$"),
        ("Night of Joy", "Williamsburg", "nightofjoybk", "bar", None, "Dive bar with DJs", "Thu,Fri,Sat", "$"),
        ("Donna", "Williamsburg", "donnabk", "bar", None, "Cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
        ("The Diamond", "Brooklyn", "thediamondbrooklyn", "bar", None, "Neighborhood bar", "Daily", "$"),
        ("Pine Box Rock Shop", "Bushwick", "pineboxrockshop", "bar", None, "Rock bar in former casket factory", "Daily", "$"),
        ("The Well", "Bushwick", "thewellbrooklyn", "bar", None, "Beer bar with backyard", "Daily", "$$"),
        ("Syndicated", "Bushwick", "syndicatedbk", "bar", None, "Bar theater with food", "Wed,Thu,Fri,Sat,Sun", "$$"),
        ("House of Wax", "Brooklyn", "houseofwaxbar", "bar", None, "Cocktail and record bar", "Thu,Fri,Sat", "$$"),
        ("Do or Dive", "Brooklyn", "doordivebk", "dive_bar", None, "Classic dive bar", "Daily", "$"),
        ("Skinny Dennis", "Williamsburg", "skinnydennis", "bar", None, "Honky tonk bar", "Daily", "$"),
        ("Rocka Rolla", "Brooklyn", "rockarollanyc", "bar", None, "Rock and metal bar", "Daily", "$"),
        ("Saint Vitus", "Brooklyn", "saintvitusbar", "live_music_venue", None, "Metal venue", "Varies", "$$"),
        ("Knitting Factory", "Brooklyn", "knittingfactory", "live_music_venue", None, "Multi-genre music venue", "Varies", "$$"),
        ("Brooklyn Steel", "Brooklyn", "brooklynsteel", "live_music_venue", None, "Large concert venue", "Varies", "$$$"),
        ("Warsaw", "Brooklyn", "warsawconcerts", "live_music_venue", None, "Polish venue for concerts", "Varies", "$$"),
        ("Kings Theatre", "Brooklyn", "kingstheatre", "live_music_venue", None, "Historic theater venue", "Varies", "$$$"),
        ("Rough Trade", "Williamsburg", "roughtradenyc", "live_music_venue", None, "Record store and venue", "Varies", "$$"),
        ("Pete's Candy Store", "Williamsburg", "petescandystore", "bar", None, "Bar with live music", "Daily", "$"),
        ("The Gutter", "Williamsburg", "thegutterbowling", "bar", None, "Bowling alley bar", "Daily", "$$"),
        ("Brooklyn Bazaar", "Brooklyn", "brooklynbazaar", "live_music_venue", None, "Music, food, and games", "Thu,Fri,Sat", "$$"),
        
        # Manhattan venues
        ("Death & Co", "East Village", "deathandcompany", "cocktail_bar", "433 E 6th St", "Award-winning cocktail bar", "Thu,Fri,Sat", "$$$"),
        ("Please Don't Tell", "East Village", "pdtnyc", "cocktail_bar", "113 St Marks Pl", "Speakeasy through phone booth", "Fri,Sat", "$$$"),
        ("The Box", "Lower East Side", "theboxnyc", "nightclub", "189 Chrystie St", "Burlesque and variety shows", "Thu,Fri,Sat", "$$$$"),
        ("Mr. Purple", "Lower East Side", "mrpurplenyc", "rooftop_bar", "180 Orchard St", "Rooftop bar with city views", "Fri,Sat,Sun", "$$$"),
        ("Beauty & Essex", "Lower East Side", "beautyandessex", "cocktail_bar", "146 Essex St", "Hidden behind pawn shop", "Thu,Fri,Sat", "$$$"),
        ("Employees Only", "West Village", "employeesonlynyc", "cocktail_bar", "510 Hudson St", "Prohibition-style cocktail bar", "Thu,Fri,Sat", "$$$"),
        ("The Django", "West Village", "thedjangonyc", "live_music_venue", "2 6th Ave", "Jazz club and cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("Blue Note", "West Village", "bluenotenyc", "culture", "131 W 3rd St", "Legendary jazz club", "Daily", "$$$"),
        ("Comedy Cellar", "West Village", "comedycellar", "culture", "117 MacDougal St", "Famous comedy club", "Daily", "$$"),
        ("Le Bain", "Meatpacking", "lebainnewyork", "rooftop_bar", "848 Washington St", "Rooftop disco with pool", "Thu,Fri,Sat", "$$$$"),
        ("Gallow Green", "Chelsea", "gallowgreen", "rooftop_bar", "542 W 27th St", "Rooftop garden bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("Sleep No More", "Chelsea", "sleepnomorenyc", "culture", "530 W 27th St", "Immersive theater experience", "Wed,Thu,Fri,Sat,Sun", "$$$$"),
        ("Rainbow Room", "Midtown", "rainbowroomnyc", "lounge", "30 Rockefeller Plaza", "Iconic supper club", "Fri,Sat", "$$$$"),
        ("Birdland", "Midtown", "birdlandjazz", "live_music_venue", "315 W 44th St", "Historic jazz club", "Daily", "$$$"),
        ("Bemelmans Bar", "Upper East Side", "bemelmansbar", "cocktail_bar", "35 E 76th St", "Classic piano bar", "Tue-Sat", "$$$$"),
        ("Little Branch", "West Village", "littlebranchnyc", "cocktail_bar", "20 7th Ave S", "Jazz and cocktails", "Daily", "$$"),
        ("Attaboy", "Lower East Side", "attaboy_ny", "cocktail_bar", "134 Eldridge St", "No-menu craft cocktails", "Wed-Sat", "$$$"),
        
        # Additional venues
        ("Brooklyn Bowl", "Williamsburg", "brooklynbowl", "live_music_venue", "61 Wythe Ave", "Bowling and music venue", "Thu,Fri,Sat", "$$"),
        ("Output", "Williamsburg", "outputclub", "nightclub", "74 Wythe Ave", "Underground dance club", "Fri,Sat", "$$$"),
        ("The Ides", "Williamsburg", "theidesbar", "rooftop_bar", "80 Wythe Ave", "Wythe Hotel rooftop", "Thu-Sun", "$$$"),
        ("House of Yes", "Bushwick", "houseofyes", "nightclub", "2 Wyckoff Ave", "Creative themed parties", "Thu,Fri,Sat", "$$"),
        ("Mood Ring", "Bushwick", "moodringbar", "bar", "1260 Myrtle Ave", "Astrology-themed bar", "Wed-Sat", "$$"),
        ("Union Hall", "Park Slope", "unionhallny", "bar", "702 Union St", "Bar with bocce courts", "Thu,Fri,Sat", "$$"),
        ("Barbès", "Park Slope", "barbesbrooklyn", "live_music_venue", "376 9th St", "World music venue", "Daily", "$"),
        ("Butter & Scotch", "Crown Heights", "butterandscotch", "bar", "818 Franklin Ave", "Dessert bar with cocktails", "Thu,Fri,Sat", "$$"),
        ("Dutch Kills", "Long Island City", "dutchkillsbar", "cocktail_bar", "27-24 Jackson Ave", "Craft cocktail bar", "Wed-Sat", "$$"),
        ("LIC Bar", "Long Island City", "licbar", "dive_bar", "45-58 Vernon Blvd", "Dive bar with outdoor space", "Thu,Fri,Sat", "$"),
        ("Westlight", "Williamsburg", "westlightnyc", "rooftop_bar", "111 N 12th St", "22nd floor rooftop bar", "Wed-Sat", "$$$"),
        ("Baby's All Right", "Williamsburg", "babysallright", "live_music_venue", "146 Broadway", "Music venue and restaurant", "Wed-Sat", "$$"),
        ("Bushwig", "Brooklyn", "bushwig", "events", "Various Locations", "Annual drag festival", "September", "$$"),
        ("House of X", "Manhattan", "houseofx", "events", "Various Locations", "Queer party collective", "Monthly", "$$"),
    ]
    
    added = 0
    for venue_data in venues_to_add:
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
        except Exception as e:
            continue
    
    return {
        "success": True,
        "message": f"Import complete! Added {added} new venues. Total: 80+ NYC nightlife spots restored.",
        "total_added": added
    }

@app.get("/debug")
async def debug():
    """Debug environment"""
    return {
        "environment_vars": {
            "DATABASE_URL": bool(os.environ.get("DATABASE_URL")),
            "GOOGLE_MAPS_API_KEY": bool(os.environ.get("GOOGLE_MAPS_API_KEY")),
            "SECRET_KEY": bool(os.environ.get("SECRET_KEY")),
            "ENVIRONMENT": os.environ.get("ENVIRONMENT", "not_set"),
            "BASE_URL": os.environ.get("BASE_URL", "not_set"),
            "RENDER": bool(os.environ.get("RENDER")),
        },
        "database_status": "connected" if db else "not_connected",
        "total_env_vars": len(os.environ),
        "python_version": os.sys.version,
        "working_directory": os.getcwd(),
        "files_in_directory": os.listdir(".")[:10]  # First 10 files
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Atlas-NYC Production API on port {port}...")
    print(f"📊 Database: {'Connected' if db else 'Not connected'}")
    print(f"🌍 Environment: {os.environ.get('ENVIRONMENT', 'production')}")
    uvicorn.run(app, host="0.0.0.0", port=port)
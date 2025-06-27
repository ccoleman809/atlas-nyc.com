from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
import sqlite3
from datetime import datetime, timedelta
import uuid
from pathlib import Path
from typing import Optional, List, Dict
from pydantic import BaseModel
from venue_db import VenueDatabase, Venue
import requests
from urllib.parse import urlparse
import mimetypes
from config import settings
import googlemaps
import logging

# Disable problematic logging in production
if settings.ENVIRONMENT == "production":
    logging.getLogger().handlers = []
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

# Create uploads directory
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

app = FastAPI(title="NYC Nightlife API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Pydantic schemas for responses
class VenueResponse(BaseModel):
    id: int
    name: str
    neighborhood: str
    instagram_handle: str
    venue_type: str
    description: Optional[str] = None
    busy_nights: Optional[str] = None
    price_range: Optional[str] = None

class ContentResponse(BaseModel):
    id: int
    venue_id: int
    content_type: str
    caption: str
    file_path: Optional[str] = None
    crowd_level: Optional[str] = None
    urgency: Optional[str] = None
    created_at: str
    expires_at: Optional[str] = None
    venue_name: str
    neighborhood: str

class SuccessResponse(BaseModel):
    success: bool
    message: str
    id: Optional[int] = None
    
class ErrorResponse(BaseModel):
    success: bool
    error: str

# Initialize databases
db = VenueDatabase()

# Initialize Google Maps client
gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY) if settings.GOOGLE_MAPS_API_KEY else None

class ContentDatabase:
    def __init__(self, db_path: str = "nightlife.db"):
        self.db_path = db_path
        self.create_content_table()
    
    def create_content_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venue_id INTEGER NOT NULL,
                content_type TEXT NOT NULL,
                caption TEXT,
                file_path TEXT,
                crowd_level TEXT,
                urgency TEXT,
                latitude REAL,
                longitude REAL,
                expires_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (venue_id) REFERENCES venues (id)
            )
        """)
        conn.commit()
        conn.close()
    
    def add_content(self, content_data: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO content (venue_id, content_type, caption, file_path, 
                                   crowd_level, urgency, latitude, longitude, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content_data['venue_id'],
                content_data['content_type'],
                content_data['caption'],
                content_data.get('file_path'),
                content_data.get('crowd_level'),
                content_data.get('urgency'),
                content_data.get('latitude'),
                content_data.get('longitude'),
                content_data.get('expires_at')
            ))
            content_id = cursor.lastrowid
            conn.commit()
            return content_id
        except Exception as e:
            print(f"Error adding content: {e}")
            return -1
        finally:
            conn.close()

content_db = ContentDatabase()

def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file and return the file path"""
    try:
        file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = uploads_dir / unique_filename
        
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        return f"uploads/{unique_filename}"
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def download_file_from_url(url: str) -> Optional[str]:
    """Download file from URL and save it locally"""
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return None
        
        # Send GET request
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        # Get content type and determine file extension
        content_type = response.headers.get('content-type', '')
        extension = mimetypes.guess_extension(content_type)
        
        # If no extension from content-type, try to get from URL
        if not extension:
            path = parsed_url.path
            if '.' in path:
                extension = '.' + path.split('.')[-1]
            else:
                # Default to jpg for images
                extension = '.jpg'
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{extension}"
        file_path = uploads_dir / unique_filename
        
        # Download and save file
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return f"uploads/{unique_filename}"
        
    except Exception as e:
        print(f"Error downloading file from URL: {e}")
        return None

# API Endpoints

@app.get("/", response_model=dict)
async def root():
    """Root endpoint - API health check"""
    return {"message": "NYC Nightlife API is running!", "version": "1.0.0"}

@app.get("/mobile", response_class=HTMLResponse)
async def get_mobile_portal():
    """Serve the mobile portal"""
    try:
        with open("mobile_portal.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Mobile portal not found")

@app.get("/public", response_class=HTMLResponse)
async def get_public_interface():
    """Serve the public magazine-style interface"""
    try:
        with open("public_interface.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Public interface not found")

@app.get("/venues")
async def get_venues(
    page: int = 1,
    per_page: int = 20,
    neighborhood: Optional[str] = None,
    venue_type: Optional[str] = None
):
    """Get venues with pagination and filtering"""
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        # Get all venues (will implement filtering in venue_db)
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
        
        return {
            "venues": [
                VenueResponse(
                    id=v.venue_id,
                    name=v.name,
                    neighborhood=v.neighborhood,
                    instagram_handle=v.instagram_handle,
                    venue_type=v.venue_type,
                    description=v.description,
                    busy_nights=v.busy_nights,
                    price_range=v.price_range
                )
                for v in page_venues
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving venues: {str(e)}")

@app.post("/venues", response_model=SuccessResponse)
async def create_venue(
    name: str = Form(..., description="Venue name"),
    neighborhood: str = Form(..., description="Neighborhood (e.g., Bushwick, LES)"),
    instagram_handle: str = Form(..., description="Instagram handle without @"),
    venue_type: str = Form(..., description="Type: dance_club, dive_bar, cocktail_lounge, etc."),
    address: Optional[str] = Form(None, description="Street address"),
    description: Optional[str] = Form(None, description="Venue description"),
    busy_nights: Optional[str] = Form(None, description="Busy nights (e.g., Thu,Fri,Sat)"),
    price_range: Optional[str] = Form(None, description="Price range: $, $$, $$$, $$$$"),
    latitude: Optional[float] = Form(None, description="GPS latitude"),
    longitude: Optional[float] = Form(None, description="GPS longitude"),
    photo: Optional[UploadFile] = File(None, description="Venue photo"),
    photo_url: Optional[str] = Form(None, description="URL to venue photo")
):
    """Create a new venue"""
    try:
        # Validate required fields
        if not name or not neighborhood or not instagram_handle or not venue_type:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Handle photo upload or URL
        photo_path = None
        if photo and photo.filename:
            photo_path = save_uploaded_file(photo)
            if not photo_path:
                raise HTTPException(status_code=500, detail="Failed to save photo")
        elif photo_url:
            photo_path = download_file_from_url(photo_url)
            if not photo_path:
                raise HTTPException(status_code=400, detail="Failed to download photo from URL")
        
        # Create venue object
        venue = Venue(
            name=name.strip(),
            neighborhood=neighborhood.strip(),
            instagram_handle=instagram_handle.strip().replace('@', ''),
            venue_type=venue_type.strip(),
            address=address.strip() if address else None,
            description=description.strip() if description else None,
            busy_nights=busy_nights.strip() if busy_nights else None,
            price_range=price_range.strip() if price_range else None
        )
        
        venue_id = db.add_venue(venue)
        
        if venue_id > 0:
            return SuccessResponse(
                success=True,
                message=f"Venue '{name}' added successfully!",
                id=venue_id
            )
        else:
            raise HTTPException(status_code=400, detail="Venue with this Instagram handle already exists")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating venue: {str(e)}")

@app.post("/content", response_model=SuccessResponse)
async def create_content(
    venue_id: int = Form(..., description="ID of the venue"),
    content_type: str = Form(..., description="Type: instagram_story, instagram_post, event, etc."),
    caption: str = Form(..., description="Content caption/description"),
    crowd_level: Optional[str] = Form(None, description="Crowd level: empty, moderate, busy, packed"),
    urgency: Optional[str] = Form(None, description="Urgency: low, medium, high, urgent"),
    latitude: Optional[float] = Form(None, description="GPS latitude"),
    longitude: Optional[float] = Form(None, description="GPS longitude"),
    file: Optional[UploadFile] = File(None, description="Image or video file"),
    file_url: Optional[str] = Form(None, description="URL to image or video file")
):
    """Create new content (Instagram post, story, or event)"""
    try:
        # Validate venue exists
        venues = db.get_all_venues()
        venue_exists = any(v.venue_id == venue_id for v in venues)
        if not venue_exists:
            raise HTTPException(status_code=404, detail=f"Venue with ID {venue_id} not found")
        
        # Handle file upload or URL
        file_path = None
        if file and file.filename:
            file_path = save_uploaded_file(file)
            if not file_path:
                raise HTTPException(status_code=500, detail="Failed to save file")
        elif file_url:
            file_path = download_file_from_url(file_url)
            if not file_path:
                raise HTTPException(status_code=400, detail="Failed to download file from URL")
        
        # Set expiration for Instagram stories
        expires_at = None
        if content_type == "instagram_story":
            expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        
        # Prepare content data
        content_data = {
            'venue_id': venue_id,
            'content_type': content_type.strip(),
            'caption': caption.strip(),
            'file_path': file_path,
            'crowd_level': crowd_level.strip() if crowd_level else None,
            'urgency': urgency.strip() if urgency else None,
            'latitude': latitude,
            'longitude': longitude,
            'expires_at': expires_at
        }
        
        content_id = content_db.add_content(content_data)
        
        if content_id > 0:
            return SuccessResponse(
                success=True,
                message=f"Content added successfully! {'(Expires in 24h)' if content_type == 'instagram_story' else ''}",
                id=content_id
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save content")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating content: {str(e)}")

@app.get("/content")
async def get_content(
    page: int = 1,
    per_page: int = 20,
    venue_id: Optional[int] = None,
    content_type: Optional[str] = None
):
    """Get content with pagination and filtering"""
    try:
        # Validate pagination
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        conn = sqlite3.connect("nightlife.db")
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
            SELECT c.*, v.name as venue_name, v.neighborhood, v.instagram_handle
            FROM content c
            JOIN venues v ON c.venue_id = v.id
            WHERE (c.expires_at IS NULL OR c.expires_at > datetime('now'))
        """
        params = []
        
        if venue_id:
            query += " AND c.venue_id = ?"
            params.append(venue_id)
        if content_type:
            query += " AND c.content_type = ?"
            params.append(content_type)
        
        # Get total count
        count_query = query.replace("SELECT c.*, v.name as venue_name, v.neighborhood, v.instagram_handle", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add ordering and pagination
        query += " ORDER BY c.timestamp DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        content_list = []
        for row in rows:
            content_list.append(ContentResponse(
                id=row[0],
                venue_id=row[1],
                content_type=row[2],
                caption=row[5] or "",
                file_path=row[3],
                crowd_level=row[6],
                urgency=row[7],
                created_at=row[10],
                expires_at=row[11],
                venue_name=row[15],
                neighborhood=row[16]
            ))
        
        return {
            "content": content_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page if total > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving content: {str(e)}")

@app.get("/content/stories", response_model=List[ContentResponse])
async def get_active_stories():
    """Get currently active Instagram stories (not expired)"""
    try:
        conn = sqlite3.connect("nightlife.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, v.name as venue_name, v.neighborhood, v.instagram_handle
            FROM content c
            JOIN venues v ON c.venue_id = v.id
            WHERE c.content_type = 'instagram_story'
            AND c.expires_at > datetime('now')
            ORDER BY c.timestamp DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        stories = []
        for row in rows:
            stories.append(ContentResponse(
                id=row[0],
                venue_id=row[1],
                content_type=row[2],
                caption=row[5] or "",
                file_path=row[3],
                crowd_level=row[6],
                urgency=row[7],
                created_at=row[10],
                expires_at=row[11],
                venue_name=row[15],
                neighborhood=row[16]
            ))
        
        return stories
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stories: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "google_maps": "enabled" if gmaps else "disabled"
    }

@app.post("/admin/init-db")
async def initialize_database():
    """Initialize database with tables (admin only)"""
    try:
        # Initialize database
        db_init = VenueDatabase()
        
        # Import NYC venues
        from import_nyc_venues import import_venues
        import_venues()
        
        return {"message": "Database initialized successfully with NYC venues"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")

@app.get("/maps/geocode")
async def geocode_address(address: str):
    """Geocode an address to get latitude and longitude"""
    if not gmaps:
        raise HTTPException(status_code=503, detail="Google Maps API not configured")
    
    try:
        result = gmaps.geocode(address)
        if not result:
            raise HTTPException(status_code=404, detail="Address not found")
        
        location = result[0]['geometry']['location']
        return {
            "address": result[0]['formatted_address'],
            "latitude": location['lat'],
            "longitude": location['lng'],
            "place_id": result[0]['place_id']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding error: {str(e)}")

@app.get("/maps/reverse-geocode")
async def reverse_geocode(lat: float, lng: float):
    """Reverse geocode coordinates to get address"""
    if not gmaps:
        raise HTTPException(status_code=503, detail="Google Maps API not configured")
    
    try:
        result = gmaps.reverse_geocode((lat, lng))
        if not result:
            raise HTTPException(status_code=404, detail="No address found for coordinates")
        
        return {
            "address": result[0]['formatted_address'],
            "latitude": lat,
            "longitude": lng,
            "place_id": result[0]['place_id']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reverse geocoding error: {str(e)}")

@app.get("/maps/nearby-places")
async def find_nearby_places(lat: float, lng: float, radius: int = 1000, place_type: str = "bar"):
    """Find nearby places using Google Places API"""
    if not gmaps:
        raise HTTPException(status_code=503, detail="Google Maps API not configured")
    
    try:
        result = gmaps.places_nearby(
            location=(lat, lng),
            radius=radius,
            type=place_type
        )
        
        places = []
        for place in result.get('results', []):
            places.append({
                "name": place.get('name'),
                "place_id": place.get('place_id'),
                "rating": place.get('rating'),
                "price_level": place.get('price_level'),
                "vicinity": place.get('vicinity'),
                "latitude": place['geometry']['location']['lat'],
                "longitude": place['geometry']['location']['lng'],
                "types": place.get('types', [])
            })
        
        return {
            "places": places,
            "next_page_token": result.get('next_page_token')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Places search error: {str(e)}")

@app.get("/maps/place-details")
async def get_place_details(place_id: str):
    """Get detailed information about a specific place"""
    if not gmaps:
        raise HTTPException(status_code=503, detail="Google Maps API not configured")
    
    try:
        result = gmaps.place(
            place_id=place_id,
            fields=['name', 'formatted_address', 'geometry', 'rating', 'price_level', 
                   'formatted_phone_number', 'website', 'opening_hours', 'photos']
        )
        
        place = result.get('result', {})
        return {
            "name": place.get('name'),
            "address": place.get('formatted_address'),
            "phone": place.get('formatted_phone_number'),
            "website": place.get('website'),
            "rating": place.get('rating'),
            "price_level": place.get('price_level'),
            "latitude": place['geometry']['location']['lat'],
            "longitude": place['geometry']['location']['lng'],
            "opening_hours": place.get('opening_hours', {}).get('weekday_text', []),
            "photos": [photo['photo_reference'] for photo in place.get('photos', [])]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Place details error: {str(e)}")

@app.get("/maps/distance-matrix")
async def calculate_distance_matrix(origins: str, destinations: str, mode: str = "walking"):
    """Calculate distance and time between multiple origins and destinations"""
    if not gmaps:
        raise HTTPException(status_code=503, detail="Google Maps API not configured")
    
    try:
        origins_list = [o.strip() for o in origins.split('|')]
        destinations_list = [d.strip() for d in destinations.split('|')]
        
        result = gmaps.distance_matrix(
            origins=origins_list,
            destinations=destinations_list,
            mode=mode,
            units="metric"
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Distance matrix error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8002))
    host = "0.0.0.0"
    
    print("🚀 Starting Atlas-NYC API server (v1.0)...")
    print(f"📱 API available at: http://{host}:{port}")
    print(f"🌐 Mobile portal at: http://{host}:{port}/mobile")
    print(f"📰 Public interface at: http://{host}:{port}/public")
    print(f"🔗 API docs available at: http://{host}:{port}/docs")
    print(f"📊 Health check at: http://{host}:{port}/health")
    
    uvicorn.run(app, host=host, port=port)

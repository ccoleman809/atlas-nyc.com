from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import sqlite3
from datetime import datetime, timedelta
import uuid
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, field_validator
import os

from venue_db import VenueDatabase, Venue
from auth import (
    Token, AdminUser, get_current_active_user, 
    verify_password, create_access_token, create_refresh_token
)
from database import db
from config import settings
from analytics import analytics_db
from analytics_middleware import AnalyticsMiddleware, AnalyticsTracker
from seo_utils import SEOHelper, SitemapGenerator
from logging_config import get_logger
from error_handlers import register_error_handlers

# Create uploads directory
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Atlas-NYC API", 
    version="2.0.0",
    description="NYC's Premier Nightlife Discovery Platform",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup logging
logger = get_logger(__name__)

# Add analytics middleware
app.add_middleware(AnalyticsMiddleware)

# Secure CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files (read-only for public)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Initialize databases
venue_db = VenueDatabase()

# Pydantic models with validation
class VenueCreate(BaseModel):
    name: str
    neighborhood: str
    instagram_handle: Optional[str] = None
    venue_type: str
    address: Optional[str] = None
    description: Optional[str] = None
    busy_nights: Optional[str] = None
    price_range: Optional[str] = None
    
    @field_validator('name', 'neighborhood', 'venue_type')
    @classmethod
    def validate_required_strings(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @field_validator('instagram_handle')
    @classmethod
    def validate_instagram(cls, v):
        if v:
            v = v.strip()
            if v.startswith('@'):
                v = v[1:]
            if not v.replace('_', '').replace('.', '').isalnum():
                raise ValueError('Invalid Instagram handle')
        return v

class ContentCreate(BaseModel):
    venue_id: int
    content_type: str
    caption: Optional[str] = None
    crowd_level: Optional[str] = None
    urgency: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v):
        allowed_types = ['post', 'story', 'reel']
        if v not in allowed_types:
            raise ValueError(f'Content type must be one of: {", ".join(allowed_types)}')
        return v
    
    @field_validator('crowd_level')
    @classmethod
    def validate_crowd_level(cls, v):
        if v:
            allowed_levels = ['empty', 'moderate', 'busy', 'packed']
            if v not in allowed_levels:
                raise ValueError(f'Crowd level must be one of: {", ".join(allowed_levels)}')
        return v

# Authentication endpoints
@app.post("/api/auth/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_admin_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    db.update_last_login(user.username)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # Log action
    user_id = db.get_admin_user_id(user.username)
    db.log_action(user_id, "login", ip_address=request.client.host)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/api/auth/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    # Validate refresh token and create new access token
    try:
        from jose import jwt
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user = db.get_admin_user(username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        access_token = create_access_token(data={"sub": username})
        new_refresh_token = create_refresh_token(data={"sub": username})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.get("/api/auth/me", response_model=AdminUser)
async def get_current_user_info(current_user: AdminUser = Depends(get_current_active_user)):
    return current_user

# Public endpoints (read-only)
@app.get("/api/venues")
@limiter.limit("30/minute")
async def get_venues(request: Request):
    """Get all venues (public endpoint)"""
    conn = sqlite3.connect('nightlife.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, neighborhood, instagram_handle, venue_type, 
               address, description, busy_nights, price_range, photo
        FROM venues
    ''')
    
    venues = []
    for row in cursor.fetchall():
        venue = dict(row)
        if venue.get('photo'):
            venue['photo'] = f"/uploads/{venue['photo']}"
        venues.append(venue)
    
    conn.close()
    return venues

@app.get("/api/content")
@limiter.limit("30/minute")
async def get_content(request: Request):
    """Get all non-expired content (public endpoint)"""
    conn = sqlite3.connect('nightlife.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.*, v.name as venue_name, v.neighborhood, v.instagram_handle
        FROM content c
        JOIN venues v ON c.venue_id = v.id
        WHERE c.expires_at IS NULL OR c.expires_at > datetime('now')
        ORDER BY c.timestamp DESC
    ''')
    
    content_items = []
    for row in cursor.fetchall():
        item = dict(row)
        if item.get('media_url'):
            # Only add /uploads/ prefix for local files, not external URLs
            if not (item['media_url'].startswith('http://') or item['media_url'].startswith('https://')):
                item['media_url'] = f"/uploads/{item['media_url']}"
        content_items.append(item)
    
    conn.close()
    return content_items

@app.get("/api/content/stories")
@limiter.limit("30/minute")
async def get_stories(request: Request):
    """Get active stories (public endpoint)"""
    conn = sqlite3.connect('nightlife.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.*, v.name as venue_name, v.neighborhood, v.instagram_handle
        FROM content c
        JOIN venues v ON c.venue_id = v.id
        WHERE c.content_type = 'story' 
        AND c.expires_at > datetime('now')
        ORDER BY c.timestamp DESC
    ''')
    
    stories = []
    for row in cursor.fetchall():
        story = dict(row)
        if story.get('media_url'):
            # Only add /uploads/ prefix for local files, not external URLs
            if not (story['media_url'].startswith('http://') or story['media_url'].startswith('https://')):
                story['media_url'] = f"/uploads/{story['media_url']}"
        stories.append(story)
    
    conn.close()
    return stories

@app.get("/api/config")
@limiter.limit("10/minute")
async def get_config(request: Request):
    """Get public configuration (API keys, etc.)"""
    return {
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        "base_url": settings.BASE_URL
    }

# Admin-only endpoints
@app.post("/api/admin/venues", status_code=201)
async def create_venue(
    request: Request,
    venue: VenueCreate,
    photo: Optional[UploadFile] = File(None),
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Create a new venue (admin only)"""
    user_id = db.get_admin_user_id(current_user.username)
    
    # Handle photo upload with security checks
    photo_filename = None
    if photo:
        # Validate file type
        file_ext = os.path.splitext(photo.filename)[1].lower()
        if file_ext not in settings.ALLOWED_FILE_TYPES[:4]:  # Only image types for venue photos
            raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed")
        
        # Validate file size
        contents = await photo.read()
        if len(contents) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        photo_filename = f"{uuid.uuid4()}{file_ext}"
        photo_path = uploads_dir / photo_filename
        
        with open(photo_path, "wb") as f:
            f.write(contents)
    
    # Create venue
    conn = sqlite3.connect('nightlife.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO venues (name, neighborhood, instagram_handle, venue_type, 
                          address, description, busy_nights, price_range, photo, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (venue.name, venue.neighborhood, venue.instagram_handle, venue.venue_type,
          venue.address, venue.description, venue.busy_nights, venue.price_range, 
          photo_filename, user_id))
    
    venue_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Log action
    db.log_action(user_id, "create_venue", "venue", venue_id, 
                  {"name": venue.name}, request.client.host)
    
    return {"id": venue_id, "message": "Venue created successfully"}

@app.put("/api/admin/venues/{venue_id}")
async def update_venue(
    request: Request,
    venue_id: int,
    venue: VenueCreate,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Update a venue (admin only)"""
    user_id = db.get_admin_user_id(current_user.username)
    
    conn = sqlite3.connect('nightlife.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE venues 
        SET name = ?, neighborhood = ?, instagram_handle = ?, venue_type = ?,
            address = ?, description = ?, busy_nights = ?, price_range = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (venue.name, venue.neighborhood, venue.instagram_handle, venue.venue_type,
          venue.address, venue.description, venue.busy_nights, venue.price_range, venue_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Venue not found")
    
    conn.commit()
    conn.close()
    
    # Log action
    db.log_action(user_id, "update_venue", "venue", venue_id, 
                  {"name": venue.name}, request.client.host)
    
    return {"message": "Venue updated successfully"}

@app.delete("/api/admin/venues/{venue_id}")
async def delete_venue(
    request: Request,
    venue_id: int,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Delete a venue (admin only)"""
    user_id = db.get_admin_user_id(current_user.username)
    
    conn = sqlite3.connect('nightlife.db')
    cursor = conn.cursor()
    
    # Get venue info for logging
    cursor.execute('SELECT name FROM venues WHERE id = ?', (venue_id,))
    venue = cursor.fetchone()
    if not venue:
        conn.close()
        raise HTTPException(status_code=404, detail="Venue not found")
    
    # Delete associated content first
    cursor.execute('DELETE FROM content WHERE venue_id = ?', (venue_id,))
    cursor.execute('DELETE FROM venues WHERE id = ?', (venue_id,))
    
    conn.commit()
    conn.close()
    
    # Log action
    db.log_action(user_id, "delete_venue", "venue", venue_id, 
                  {"name": venue[0]}, request.client.host)
    
    return {"message": "Venue deleted successfully"}

@app.post("/api/admin/content", status_code=201)
async def create_content(
    request: Request,
    content: ContentCreate,
    file: UploadFile = File(...),
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Create new content (admin only)"""
    user_id = db.get_admin_user_id(current_user.username)
    
    # Validate file
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed")
    
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Save file
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = uploads_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Determine media type
    media_type = 'video' if file_ext in ['.mp4', '.mov'] else 'image'
    
    # Set expiration for stories
    expires_at = None
    if content.content_type == 'story':
        expires_at = datetime.now() + timedelta(hours=24)
    
    # Insert into database
    conn = sqlite3.connect('nightlife.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO content (venue_id, content_type, media_url, media_type, caption,
                           crowd_level, urgency, latitude, longitude, expires_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (content.venue_id, content.content_type, filename, media_type, content.caption,
          content.crowd_level, content.urgency, content.latitude, content.longitude,
          expires_at, user_id))
    
    content_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Log action
    db.log_action(user_id, "create_content", "content", content_id,
                  {"venue_id": content.venue_id, "type": content.content_type}, 
                  request.client.host)
    
    return {"id": content_id, "message": "Content created successfully"}

@app.delete("/api/admin/content/{content_id}")
async def delete_content(
    request: Request,
    content_id: int,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Delete content (admin only)"""
    user_id = db.get_admin_user_id(current_user.username)
    
    conn = sqlite3.connect('nightlife.db')
    cursor = conn.cursor()
    
    # Get content info
    cursor.execute('SELECT media_url, venue_id FROM content WHERE id = ?', (content_id,))
    content = cursor.fetchone()
    if not content:
        conn.close()
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Delete from database
    cursor.execute('DELETE FROM content WHERE id = ?', (content_id,))
    conn.commit()
    conn.close()
    
    # Delete file
    if content[0]:
        file_path = uploads_dir / content[0]
        if file_path.exists():
            file_path.unlink()
    
    # Log action
    db.log_action(user_id, "delete_content", "content", content_id,
                  {"venue_id": content[1]}, request.client.host)
    
    return {"message": "Content deleted successfully"}

@app.get("/api/admin/audit-log")
async def get_audit_log(
    request: Request,
    limit: int = 100,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Get audit log (admin only)"""
    conn = sqlite3.connect('nightlife.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.*, u.username
        FROM audit_log a
        JOIN admin_users u ON a.user_id = u.id
        ORDER BY a.timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return logs

# Analytics endpoints (admin only)
@app.get("/api/admin/analytics/global")
async def get_global_analytics(
    request: Request,
    days: int = 30,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Get global platform analytics (admin only)"""
    analytics_data = analytics_db.get_global_analytics(days)
    
    # Log admin action
    user_id = db.get_admin_user_id(current_user.username)
    db.log_action(user_id, "view_global_analytics", None, None, 
                  {"days": days}, request.client.host)
    
    return analytics_data

@app.get("/api/admin/analytics/venues/{venue_id}")
async def get_venue_analytics(
    request: Request,
    venue_id: int,
    days: int = 30,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Get analytics for a specific venue (admin only)"""
    analytics_data = analytics_db.get_venue_analytics(venue_id, days)
    
    # Log admin action
    user_id = db.get_admin_user_id(current_user.username)
    db.log_action(user_id, "view_venue_analytics", "venue", venue_id,
                  {"days": days}, request.client.host)
    
    return analytics_data

@app.get("/api/admin/analytics/content/{content_id}")
async def get_content_analytics(
    request: Request,
    content_id: int,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Get analytics for specific content (admin only)"""
    analytics_data = analytics_db.get_content_analytics(content_id)
    
    # Log admin action
    user_id = db.get_admin_user_id(current_user.username)
    db.log_action(user_id, "view_content_analytics", "content", content_id,
                  {}, request.client.host)
    
    return analytics_data

@app.get("/api/admin/analytics/performance")
async def get_performance_metrics(
    request: Request,
    hours: int = 24,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Get performance metrics (admin only)"""
    metrics = analytics_db.get_performance_metrics(hours)
    
    # Log admin action
    user_id = db.get_admin_user_id(current_user.username)
    db.log_action(user_id, "view_performance_metrics", None, None,
                  {"hours": hours}, request.client.host)
    
    return metrics

@app.get("/api/admin/analytics/realtime")
async def get_realtime_analytics(
    request: Request,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Get real-time analytics dashboard data (admin only)"""
    from datetime import datetime, timedelta
    import sqlite3
    
    # Get active sessions (last 30 minutes)
    thirty_min_ago = datetime.now() - timedelta(minutes=30)
    
    conn = sqlite3.connect('nightlife.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Active sessions
    cursor.execute('''
        SELECT COUNT(*) as active_sessions
        FROM user_sessions 
        WHERE last_activity >= ?
    ''', (thirty_min_ago,))
    active_sessions = cursor.fetchone()[0]
    
    # Recent events (last hour)
    one_hour_ago = datetime.now() - timedelta(hours=1)
    cursor.execute('''
        SELECT COUNT(*) as recent_events
        FROM analytics_events
        WHERE timestamp >= ?
    ''', (one_hour_ago,))
    recent_events = cursor.fetchone()[0]
    
    # Top venues in last hour
    cursor.execute('''
        SELECT v.name, COUNT(*) as views
        FROM analytics_events ae
        JOIN venues v ON ae.venue_id = v.id
        WHERE ae.timestamp >= ? AND ae.event_type = 'venue_view'
        GROUP BY v.id
        ORDER BY views DESC
        LIMIT 5
    ''', (one_hour_ago,))
    top_venues_hour = [dict(row) for row in cursor.fetchall()]
    
    # Recent searches
    cursor.execute('''
        SELECT search_term, COUNT(*) as frequency
        FROM search_analytics
        WHERE timestamp >= ?
        GROUP BY search_term
        ORDER BY frequency DESC
        LIMIT 10
    ''', (one_hour_ago,))
    recent_searches = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Log admin action
    user_id = db.get_admin_user_id(current_user.username)
    db.log_action(user_id, "view_realtime_analytics", None, None, {}, request.client.host)
    
    return {
        "active_sessions": active_sessions,
        "recent_events": recent_events,
        "top_venues_hour": top_venues_hour,
        "recent_searches": recent_searches,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/admin/analytics/export")
async def export_analytics(
    request: Request,
    export_type: str,
    start_date: str,
    end_date: str,
    venue_ids: Optional[List[int]] = None,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """Export analytics data (admin only)"""
    import csv
    import io
    from datetime import datetime
    
    # Validate export type
    if export_type not in ['venues', 'content', 'events', 'sessions']:
        raise HTTPException(status_code=400, detail="Invalid export type")
    
    # Parse dates
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    conn = sqlite3.connect('nightlife.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Prepare CSV data based on export type
    if export_type == 'venues':
        query = '''
            SELECT v.name, v.neighborhood, v.venue_type,
                   SUM(dvs.views) as total_views,
                   SUM(dvs.unique_visitors) as unique_visitors,
                   SUM(dvs.content_views) as content_views
            FROM venues v
            LEFT JOIN daily_venue_stats dvs ON v.id = dvs.venue_id
            WHERE dvs.date BETWEEN ? AND ?
        '''
        params = [start_dt.date(), end_dt.date()]
        
        if venue_ids:
            query += ' AND v.id IN ({})'.format(','.join(['?' for _ in venue_ids]))
            params.extend(venue_ids)
            
        query += ' GROUP BY v.id ORDER BY total_views DESC'
        
    elif export_type == 'events':
        query = '''
            SELECT ae.event_type, ae.timestamp, v.name as venue_name,
                   ae.ip_address, ae.properties
            FROM analytics_events ae
            LEFT JOIN venues v ON ae.venue_id = v.id
            WHERE ae.timestamp BETWEEN ? AND ?
            ORDER BY ae.timestamp DESC
        '''
        params = [start_dt, end_dt]
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Create CSV
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))
    
    csv_content = output.getvalue()
    output.close()
    
    # Log admin action
    user_id = db.get_admin_user_id(current_user.username)
    db.log_action(user_id, "export_analytics", None, None,
                  {"export_type": export_type, "start_date": start_date, "end_date": end_date},
                  request.client.host)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=analytics_{export_type}_{start_date}_{end_date}.csv"}
    )

# Public content creation endpoints
@app.post("/api/content", status_code=201)
@limiter.limit("30/minute")
async def create_content_public(
    request: Request,
    venue_id: int = Form(...),
    content_type: str = Form(...),
    caption: Optional[str] = Form(None),
    crowd_level: Optional[str] = Form(None),
    urgency: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    file: Optional[UploadFile] = File(None),
    file_url: Optional[str] = Form(None)
):
    """Create new content (public endpoint with rate limiting)"""
    
    try:
        # Validate content type
        if content_type not in ['post', 'story', 'reel']:
            raise HTTPException(status_code=400, detail="Invalid content type")
        
        # Validate venue exists
        conn = sqlite3.connect('nightlife.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM venues WHERE id = ?', (venue_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Venue not found")
        
        # Handle file upload or URL
        filename = None
        media_type = None
        
        if file and file.filename:
            # Handle file upload
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in settings.ALLOWED_FILE_TYPES:
                conn.close()
                raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed")
            
            contents = await file.read()
            if len(contents) > settings.MAX_UPLOAD_SIZE:
                conn.close()
                raise HTTPException(status_code=400, detail=f"File too large (max {settings.MAX_UPLOAD_SIZE/1024/1024:.1f}MB)")
            
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = uploads_dir / filename
            
            with open(file_path, "wb") as f:
                f.write(contents)
            
            media_type = 'video' if file_ext in ['.mp4', '.mov'] else 'image'
            
        elif file_url and file_url.strip():
            # Handle URL - store the URL directly instead of downloading
            filename = file_url.strip()
            
            # Determine media type from URL
            if any(ext in filename.lower() for ext in ['.mp4', '.mov', '.webm', '.avi']):
                media_type = 'video'
            elif any(ext in filename.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                media_type = 'image'
            else:
                media_type = 'unknown'
        
        # Set expiration for stories
        expires_at = None
        if content_type == 'story':
            expires_at = datetime.now() + timedelta(hours=24)
        
        # Insert into database
        cursor.execute('''
            INSERT INTO content (venue_id, content_type, media_url, media_type, caption,
                               crowd_level, urgency, latitude, longitude, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (venue_id, content_type, filename, media_type, caption,
              crowd_level, urgency, latitude, longitude, expires_at))
        
        content_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Content created successfully: ID {content_id}, type {content_type}, venue {venue_id}")
        
        return {
            "id": content_id, 
            "message": f"Content created successfully! {'(Expires in 24h)' if content_type == 'story' else ''}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating content: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/api/venues", status_code=201)
@limiter.limit("15/minute")
async def create_venue_public(
    request: Request,
    name: str = Form(...),
    neighborhood: str = Form(...),
    instagram_handle: Optional[str] = Form(None),
    venue_type: str = Form(...),
    address: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    busy_nights: Optional[str] = Form(None),
    price_range: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None)
):
    """Create a new venue (public endpoint with rate limiting)"""
    
    # Basic validation
    if not name or not neighborhood or not venue_type:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Handle photo upload
    photo_filename = None
    if photo and photo.filename:
        file_ext = os.path.splitext(photo.filename)[1].lower()
        if file_ext not in ['.jpg', '.jpeg', '.png', '.gif']:
            raise HTTPException(status_code=400, detail="Photo must be JPG, PNG, or GIF")
        
        contents = await photo.read()
        if len(contents) > 5 * 1024 * 1024:  # 5MB limit for photos
            raise HTTPException(status_code=400, detail="Photo too large (max 5MB)")
        
        photo_filename = f"{uuid.uuid4()}{file_ext}"
        photo_path = uploads_dir / photo_filename
        
        with open(photo_path, "wb") as f:
            f.write(contents)
    
    # Clean Instagram handle
    if instagram_handle:
        instagram_handle = instagram_handle.strip().replace('@', '')
    
    # Insert into database
    conn = sqlite3.connect('nightlife.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO venues (name, neighborhood, instagram_handle, venue_type, 
                              address, description, busy_nights, price_range, photo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name.strip(), neighborhood.strip(), instagram_handle, venue_type.strip(),
              address.strip() if address else None, 
              description.strip() if description else None,
              busy_nights.strip() if busy_nights else None,
              price_range.strip() if price_range else None,
              photo_filename))
        
        venue_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {"id": venue_id, "message": f"Venue '{name}' created successfully!"}
        
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Venue with this Instagram handle already exists")
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error creating venue: {str(e)}")

# Public analytics endpoints (limited data)
@app.post("/api/track/search")
@limiter.limit("60/minute")
async def track_search_public(
    request: Request,
    search_data: dict
):
    """Track search queries (public endpoint with rate limiting)"""
    search_term = search_data.get("search_term", "").strip()
    search_type = search_data.get("search_type")
    results_count = search_data.get("results_count", 0)
    
    if search_term:
        AnalyticsTracker.track_search(search_term, search_type, results_count)
    
    return {"status": "tracked"}

@app.post("/api/track/share")
@limiter.limit("30/minute")
async def track_share_public(
    request: Request,
    share_data: dict
):
    """Track share events (public endpoint with rate limiting)"""
    venue_id = share_data.get("venue_id")
    content_id = share_data.get("content_id")
    platform = share_data.get("platform")
    session_id = request.headers.get("X-Session-ID")
    
    AnalyticsTracker.track_share(
        venue_id=venue_id,
        content_id=content_id,
        platform=platform,
        session_id=session_id,
        ip_address=request.client.host
    )
    
    return {"status": "tracked"}

@app.post("/api/track/favorite")
@limiter.limit("30/minute")
async def track_favorite_public(
    request: Request,
    favorite_data: dict
):
    """Track favorite events (public endpoint with rate limiting)"""
    venue_id = favorite_data.get("venue_id")
    content_id = favorite_data.get("content_id")
    session_id = request.headers.get("X-Session-ID")
    
    AnalyticsTracker.track_favorite(
        venue_id=venue_id,
        content_id=content_id,
        session_id=session_id,
        ip_address=request.client.host
    )
    
    return {"status": "tracked"}

@app.post("/api/track/venue-view")
@limiter.limit("60/minute")
async def track_venue_view_public(
    request: Request,
    view_data: dict
):
    """Track venue page views (public endpoint with rate limiting)"""
    venue_id = view_data.get("venue_id")
    venue_name = view_data.get("venue_name")
    session_id = request.headers.get("X-Session-ID")
    
    if venue_id:
        AnalyticsTracker.track_click(
            element="venue_page_view",
            venue_id=venue_id,
            session_id=session_id,
            ip_address=request.client.host
        )
    
    return {"status": "tracked"}

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        conn = sqlite3.connect('nightlife.db')
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "environment": settings.ENVIRONMENT,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# SEO and Public Pages
@app.get("/robots.txt", response_class=Response)
async def robots_txt():
    """Serve robots.txt for SEO"""
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/admin/
Disallow: /uploads/

Sitemap: {SEOHelper.BASE_URL}/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")

@app.get("/sitemap.xml", response_class=Response)
async def sitemap_xml():
    """Generate and serve main sitemap"""
    sitemap = SitemapGenerator.generate_sitemap_index()
    return Response(content=sitemap, media_type="application/xml")

@app.get("/sitemap-main.xml", response_class=Response)
async def sitemap_main():
    """Generate and serve main pages sitemap"""
    sitemap = SitemapGenerator.generate_main_sitemap()
    return Response(content=sitemap, media_type="application/xml")

@app.get("/sitemap-venues.xml", response_class=Response)
async def sitemap_venues():
    """Generate and serve venues sitemap"""
    # Get all venues
    conn = sqlite3.connect('nightlife.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM venues')
    venues = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    sitemap = SitemapGenerator.generate_venues_sitemap(venues)
    return Response(content=sitemap, media_type="application/xml")

@app.get("/venues/{venue_slug}", response_class=HTMLResponse)
async def venue_detail_page(venue_slug: str, request: Request):
    """Serve SEO-optimized venue detail page"""
    # Extract venue ID from slug
    venue_id = int(venue_slug.split('-')[-1])
    
    # Get venue data
    conn = sqlite3.connect('nightlife.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM venues WHERE id = ?', (venue_id,))
    venue = cursor.fetchone()
    conn.close()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    venue_dict = dict(venue)
    
    # Generate SEO data
    title = SEOHelper.generate_meta_title("venue", venue_dict['name'], venue_dict['neighborhood'])
    description = SEOHelper.generate_meta_description("venue", venue_dict)
    canonical_url = SEOHelper.generate_canonical_url(request)
    structured_data = SEOHelper.generate_venue_structured_data(venue_dict)
    og_tags = SEOHelper.generate_open_graph_tags("venue", title, description, canonical_url, 
                                                 f"{SEOHelper.BASE_URL}/uploads/{venue_dict['photo']}" if venue_dict['photo'] else None, 
                                                 venue_dict)
    keywords = SEOHelper.generate_keywords("venue", venue_dict)
    
    # Breadcrumbs
    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Venues", "url": "/venues"},
        {"name": venue_dict['neighborhood'], "url": f"/neighborhoods/{SEOHelper.clean_text_for_seo(venue_dict['neighborhood'])}"},
        {"name": venue_dict['name'], "url": f"/venues/{venue_slug}"}
    ]
    breadcrumb_schema = SEOHelper.generate_breadcrumb_structured_data(breadcrumbs)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <link rel="canonical" href="{canonical_url}">
    
    <!-- Open Graph / Facebook -->
    {''.join([f'<meta property="{key}" content="{value}">' for key, value in og_tags.items() if key.startswith('og:')])}
    
    <!-- Twitter -->
    {''.join([f'<meta name="{key}" content="{value}">' for key, value in og_tags.items() if key.startswith('twitter:')])}
    
    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">{json.dumps(structured_data, indent=2)}</script>
    <script type="application/ld+json">{json.dumps(breadcrumb_schema, indent=2)}</script>
    
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .hero {{ background: #1a1a1a; color: white; padding: 3rem; border-radius: 10px; margin-bottom: 2rem; }}
        .venue-name {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .venue-type {{ font-size: 1.2rem; opacity: 0.8; }}
        .content {{ display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; }}
        .main-content {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .sidebar {{ background: #f8f9fa; padding: 2rem; border-radius: 10px; }}
        .info-item {{ margin-bottom: 1rem; }}
        .label {{ font-weight: bold; color: #333; }}
        .breadcrumb {{ margin-bottom: 2rem; }}
        .breadcrumb a {{ color: #007bff; text-decoration: none; }}
        .breadcrumb a:hover {{ text-decoration: underline; }}
        @media (max-width: 768px) {{ .content {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="breadcrumb">
            {''.join([f'<a href="{crumb["url"]}">{crumb["name"]}</a>' + (' > ' if i < len(breadcrumbs)-1 else '') for i, crumb in enumerate(breadcrumbs)])}
        </nav>
        
        <header class="hero">
            <h1 class="venue-name">{venue_dict['name']}</h1>
            <p class="venue-type">{venue_dict['venue_type'].title()} • {venue_dict['neighborhood']}</p>
        </header>
        
        <div class="content">
            <main class="main-content">
                <h2>About {venue_dict['name']}</h2>
                <p>{venue_dict.get('description', f"Experience {venue_dict['name']}, one of {venue_dict['neighborhood']}'s premier {venue_dict['venue_type']} destinations in NYC's vibrant nightlife scene.")}</p>
                
                <h3>What to Expect</h3>
                <p>Located in the heart of {venue_dict['neighborhood']}, {venue_dict['name']} offers an authentic NYC nightlife experience. Whether you're looking for craft cocktails, dancing, or a sophisticated atmosphere, this {venue_dict['venue_type']} delivers.</p>
                
                {'<h3>Address</h3><p>' + venue_dict['address'] + '</p>' if venue_dict.get('address') else ''}
                {'<h3>Busy Nights</h3><p>' + venue_dict['busy_nights'] + '</p>' if venue_dict.get('busy_nights') else ''}
            </main>
            
            <aside class="sidebar">
                <h3>Quick Info</h3>
                <div class="info-item">
                    <span class="label">Type:</span> {venue_dict['venue_type'].title()}
                </div>
                <div class="info-item">
                    <span class="label">Neighborhood:</span> {venue_dict['neighborhood']}
                </div>
                {'<div class="info-item"><span class="label">Price Range:</span> ' + venue_dict['price_range'] + '</div>' if venue_dict.get('price_range') else ''}
                {'<div class="info-item"><span class="label">Instagram:</span> <a href="https://instagram.com/' + venue_dict['instagram_handle'] + '" target="_blank">@' + venue_dict['instagram_handle'] + '</a></div>' if venue_dict.get('instagram_handle') else ''}
                
                <h3>Explore More</h3>
                <p><a href="/venues">Browse all venues</a></p>
                <p><a href="/neighborhoods/{SEOHelper.clean_text_for_seo(venue_dict['neighborhood'])}">Explore {venue_dict['neighborhood']}</a></p>
            </aside>
        </div>
    </div>
    
    <script>
        // Track venue view
        fetch('/api/track/venue-view', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ venue_id: {venue_id}, venue_name: '{venue_dict['name']}' }})
        }}).catch(console.error);
    </script>
</body>
</html>"""
    
    return html_content

@app.get("/neighborhoods/{neighborhood_slug}", response_class=HTMLResponse)
async def neighborhood_page(neighborhood_slug: str, request: Request):
    """Serve SEO-optimized neighborhood page"""
    neighborhood_name = neighborhood_slug.replace('-', ' ').title()
    
    # Get venues in this neighborhood
    conn = sqlite3.connect('nightlife.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM venues WHERE LOWER(neighborhood) = LOWER(?)', (neighborhood_name,))
    venues = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not venues:
        raise HTTPException(status_code=404, detail="Neighborhood not found")
    
    # Generate SEO data
    title = SEOHelper.generate_meta_title("neighborhood", neighborhood_name)
    description = SEOHelper.generate_meta_description("neighborhood", {"name": neighborhood_name})
    canonical_url = SEOHelper.generate_canonical_url(request)
    keywords = SEOHelper.generate_keywords("neighborhood", {"name": neighborhood_name})
    
    # Breadcrumbs
    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Neighborhoods", "url": "/neighborhoods"},
        {"name": neighborhood_name, "url": f"/neighborhoods/{neighborhood_slug}"}
    ]
    breadcrumb_schema = SEOHelper.generate_breadcrumb_structured_data(breadcrumbs)
    
    venue_types = list(set([venue['venue_type'] for venue in venues]))
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <link rel="canonical" href="{canonical_url}">
    
    <script type="application/ld+json">{json.dumps(breadcrumb_schema, indent=2)}</script>
    
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .hero {{ background: #1a1a1a; color: white; padding: 3rem; border-radius: 10px; margin-bottom: 2rem; text-align: center; }}
        .venue-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 2rem; }}
        .venue-card {{ background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .venue-name {{ font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem; }}
        .venue-type {{ color: #666; margin-bottom: 1rem; }}
        .breadcrumb {{ margin-bottom: 2rem; }}
        .breadcrumb a {{ color: #007bff; text-decoration: none; }}
        .stats {{ display: flex; gap: 2rem; justify-content: center; margin: 2rem 0; }}
        .stat {{ text-align: center; }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: #007bff; }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="breadcrumb">
            {''.join([f'<a href="{crumb["url"]}">{crumb["name"]}</a>' + (' > ' if i < len(breadcrumbs)-1 else '') for i, crumb in enumerate(breadcrumbs)])}
        </nav>
        
        <header class="hero">
            <h1>{neighborhood_name} Nightlife Guide</h1>
            <p>Discover the best bars, clubs, and entertainment in {neighborhood_name}</p>
        </header>
        
        <main>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{len(venues)}</div>
                    <div>Venues</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{len(venue_types)}</div>
                    <div>Types</div>
                </div>
            </div>
            
            <h2>Top Venues in {neighborhood_name}</h2>
            <div class="venue-grid">
                {''.join([f'''
                <article class="venue-card">
                    <h3 class="venue-name">
                        <a href="/venues/{SEOHelper.generate_venue_slug(venue["name"], venue["id"])}" style="text-decoration: none; color: inherit;">
                            {venue["name"]}
                        </a>
                    </h3>
                    <p class="venue-type">{venue["venue_type"].title()}</p>
                    <p>{venue.get("description", f"Experience {venue['name']} in {neighborhood_name}")[:100]}...</p>
                </article>
                ''' for venue in venues[:12]])}
            </div>
        </main>
    </div>
</body>
</html>"""
    
    return html_content

# Serve HTML interfaces
@app.get("/", response_class=HTMLResponse)
async def read_public_interface():
    """Serve the SEO-optimized Atlas-NYC public interface"""
    with open("atlas_public_interface.html", "r") as f:
        return f.read()

@app.get("/admin", response_class=HTMLResponse)
async def read_admin_interface():
    """Serve the admin login interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NYC Nightlife Admin</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .login-form { 
                max-width: 300px; 
                margin: 50px auto; 
                background: white; 
                padding: 2rem; 
                border-radius: 8px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h2 { text-align: center; margin-bottom: 1.5rem; }
            input { 
                width: 100%; 
                padding: 10px; 
                margin: 8px 0; 
                border: 1px solid #ddd; 
                border-radius: 4px;
                font-size: 1rem;
            }
            button { 
                width: 100%; 
                padding: 12px; 
                background: #007bff; 
                color: white; 
                border: none; 
                border-radius: 4px;
                cursor: pointer; 
                font-size: 1rem;
                transition: background 0.3s;
            }
            button:hover { background: #0056b3; }
            #error { text-align: center; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="login-form">
            <h2>Admin Login</h2>
            <form id="loginForm">
                <input type="text" id="username" placeholder="Username" required>
                <input type="password" id="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p id="error" style="color: red;"></p>
        </div>
        <script>
            document.getElementById('loginForm').onsubmit = async (e) => {
                e.preventDefault();
                const formData = new FormData();
                formData.append('username', document.getElementById('username').value);
                formData.append('password', document.getElementById('password').value);
                
                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        localStorage.setItem('access_token', data.access_token);
                        localStorage.setItem('refresh_token', data.refresh_token);
                        window.location.href = '/admin/dashboard';
                    } else {
                        document.getElementById('error').textContent = 'Invalid credentials';
                    }
                } catch (error) {
                    document.getElementById('error').textContent = 'Login failed';
                }
            };
        </script>
    </body>
    </html>
    """

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def read_admin_dashboard():
    """Serve the admin dashboard"""
    with open("admin_dashboard.html", "r") as f:
        return f.read()

@app.get("/mobile", response_class=HTMLResponse)
async def read_mobile_portal():
    """Serve the mobile portal"""
    try:
        with open("mobile_portal.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Mobile portal not found")

@app.get("/public", response_class=HTMLResponse)
async def read_public_interface():
    """Serve the public interface"""
    try:
        with open("public_interface.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Public interface not found")

@app.get("/docs", response_class=HTMLResponse)
async def read_api_docs():
    """Redirect to API documentation"""
    return f'<script>window.location.href="/api/docs";</script>'

if __name__ == "__main__":
    import uvicorn
    print("Starting NYC Nightlife Secure API Server...")
    print("Admin endpoints are now protected with authentication")
    print("Create an admin user with: python create_admin.py")
    uvicorn.run(app, host="0.0.0.0", port=8001)
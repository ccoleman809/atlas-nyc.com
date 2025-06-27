# Atlas-NYC API Documentation

## Overview
The Atlas-NYC API provides endpoints for managing NYC nightlife venues and content. This RESTful API supports venue management, content creation, and Google Maps integration.

## Base URL
- Development: `http://localhost:8002`
- Production: `https://your-domain.com`

## Authentication
Currently, the API does not require authentication for read operations. Write operations are open but should be secured in production.

## Endpoints

### Health Check
**GET** `/health`
- Returns API health status
- Response: `{"status": "healthy", "timestamp": "...", "database": "connected", "google_maps": "enabled"}`

### Venues

#### Get All Venues
**GET** `/venues`

Query Parameters:
- `page` (int, default: 1) - Page number
- `per_page` (int, default: 20, max: 100) - Items per page
- `neighborhood` (string, optional) - Filter by neighborhood
- `venue_type` (string, optional) - Filter by venue type

Response:
```json
{
  "venues": [
    {
      "id": 1,
      "name": "House of Yes",
      "neighborhood": "Bushwick",
      "instagram_handle": "houseofyes",
      "venue_type": "nightclub",
      "description": "Creative nightclub with themed parties",
      "busy_nights": "Thu,Fri,Sat",
      "price_range": "$$$"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 25,
    "pages": 2
  }
}
```

#### Create Venue
**POST** `/venues`

Form Data:
- `name` (required) - Venue name (max 100 chars)
- `neighborhood` (required) - Neighborhood (max 50 chars)
- `instagram_handle` (required) - Instagram handle without @ (max 30 chars)
- `venue_type` (required) - One of: nightclub, bar, cocktail_bar, dive_bar, rooftop_bar, lounge, live_music_venue
- `address` (optional) - Street address
- `description` (optional) - Venue description
- `busy_nights` (optional) - Busy nights (e.g., "Thu,Fri,Sat")
- `price_range` (optional) - One of: $, $$, $$$, $$$$
- `latitude` (optional) - GPS latitude
- `longitude` (optional) - GPS longitude
- `photo` (optional) - Venue photo file
- `photo_url` (optional) - URL to venue photo

Response:
```json
{
  "success": true,
  "message": "Venue 'House of Yes' added successfully!",
  "id": 1
}
```

### Content

#### Get Content
**GET** `/content`

Query Parameters:
- `page` (int, default: 1) - Page number
- `per_page` (int, default: 20, max: 100) - Items per page
- `venue_id` (int, optional) - Filter by venue ID
- `content_type` (string, optional) - Filter by content type

#### Create Content
**POST** `/content`

Form Data:
- `venue_id` (required) - ID of the venue
- `content_type` (required) - One of: instagram_story, instagram_post, event, photo, video
- `caption` (required) - Content caption (max 500 chars)
- `crowd_level` (optional) - One of: empty, moderate, busy, packed
- `urgency` (optional) - One of: low, medium, high, urgent
- `latitude` (optional) - GPS latitude
- `longitude` (optional) - GPS longitude
- `file` (optional) - Image or video file
- `file_url` (optional) - URL to image or video file

#### Get Active Stories
**GET** `/content/stories`
- Returns currently active Instagram stories (not expired)

### Google Maps Integration

#### Geocode Address
**GET** `/maps/geocode?address={address}`
- Convert address to coordinates
- Returns: address, latitude, longitude, place_id

#### Reverse Geocode
**GET** `/maps/reverse-geocode?lat={lat}&lng={lng}`
- Convert coordinates to address
- Returns: address, latitude, longitude, place_id

#### Find Nearby Places
**GET** `/maps/nearby-places?lat={lat}&lng={lng}&radius={radius}&place_type={type}`
- Find nearby places using Google Places API
- Default radius: 1000m, default type: "bar"

#### Get Place Details
**GET** `/maps/place-details?place_id={place_id}`
- Get detailed information about a specific place

#### Distance Matrix
**GET** `/maps/distance-matrix?origins={origins}&destinations={destinations}&mode={mode}`
- Calculate distance and time between locations
- Origins and destinations separated by "|"
- Mode: walking, driving, transit, bicycling

### Static Files

#### Mobile Portal
**GET** `/mobile` - Mobile interface for venue and content management

#### Public Interface
**GET** `/public` - Public-facing magazine-style interface

#### Uploaded Files
**GET** `/uploads/{filename}` - Access uploaded images and files

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error description"
}
```

Common HTTP status codes:
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (Google Maps API not configured)

## Data Validation

### Venue Types
- nightclub
- bar
- cocktail_bar
- dive_bar
- rooftop_bar
- lounge
- live_music_venue

### Content Types
- instagram_story
- instagram_post
- event
- photo
- video

### Crowd Levels
- empty
- moderate
- busy
- packed

### Urgency Levels
- low
- medium
- high
- urgent

### Price Ranges
- $ (Budget-friendly)
- $$ (Moderate)
- $$$ (Expensive)
- $$$$ (Very expensive)

## Rate Limiting
Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## CORS
CORS is enabled for all origins (`*`). Restrict this in production for security.
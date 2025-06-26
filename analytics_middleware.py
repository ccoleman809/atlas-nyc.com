from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
from datetime import datetime
from analytics import analytics_db, AnalyticsEvent, EventType
import re
from typing import Optional

class AnalyticsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.start_time = time.time()
    
    async def dispatch(self, request: Request, call_next):
        # Start timing the request
        start_time = time.time()
        
        # Get or create session ID
        session_id = self._get_session_id(request)
        
        # Extract client info
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        referrer = request.headers.get("referer")
        
        # Update session
        analytics_db.update_session(session_id)
        
        # Process the request
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Track the request analytics
        await self._track_request(request, response, session_id, ip_address, user_agent, referrer, process_time)
        
        # Add session ID to response headers (for client-side tracking)
        response.headers["X-Session-ID"] = session_id
        
        return response
    
    def _get_session_id(self, request: Request) -> str:
        """Get or generate session ID"""
        # Try to get from cookie first
        session_id = request.cookies.get("session_id")
        
        if not session_id:
            # Generate new session ID
            session_id = str(uuid.uuid4())
            
            # Start new session in database
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")
            referrer = request.headers.get("referer")
            
            analytics_db.start_session(session_id, ip_address, user_agent, referrer)
        
        return session_id
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers (behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return request.client.host if request.client else "unknown"
    
    async def _track_request(self, request: Request, response: Response, session_id: str, 
                           ip_address: str, user_agent: str, referrer: str, process_time: float):
        """Track request analytics"""
        path = request.url.path
        method = request.method
        status_code = response.status_code
        
        # Only track successful GET requests to avoid noise
        if method != "GET" or status_code >= 400:
            return
        
        # Parse venue and content IDs from URL
        venue_id = self._extract_venue_id(path, request.query_params)
        content_id = self._extract_content_id(path, request.query_params)
        
        # Determine event type based on path
        event_type = self._determine_event_type(path)
        
        if event_type:
            # Track the main event
            event = AnalyticsEvent(
                event_type=event_type,
                venue_id=venue_id,
                content_id=content_id,
                user_session=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer,
                properties={
                    "path": path,
                    "method": method,
                    "status_code": status_code,
                    "response_time_ms": round(process_time * 1000, 2),
                    "query_params": dict(request.query_params)
                }
            )
            
            analytics_db.track_event(event)
        
        # Track performance metrics
        analytics_db.record_performance_metric(
            "response_time",
            process_time,
            {
                "endpoint": path,
                "method": method,
                "status_code": status_code
            }
        )
    
    def _extract_venue_id(self, path: str, query_params) -> Optional[int]:
        """Extract venue ID from path or query parameters"""
        # Check query parameters first
        venue_id = query_params.get("venue_id")
        if venue_id:
            try:
                return int(venue_id)
            except ValueError:
                pass
        
        # Check for venue ID in path
        venue_match = re.search(r'/venues/(\d+)', path)
        if venue_match:
            return int(venue_match.group(1))
        
        return None
    
    def _extract_content_id(self, path: str, query_params) -> Optional[int]:
        """Extract content ID from path or query parameters"""
        # Check query parameters first
        content_id = query_params.get("content_id")
        if content_id:
            try:
                return int(content_id)
            except ValueError:
                pass
        
        # Check for content ID in path
        content_match = re.search(r'/content/(\d+)', path)
        if content_match:
            return int(content_match.group(1))
        
        return None
    
    def _determine_event_type(self, path: str) -> Optional[str]:
        """Determine event type based on request path"""
        if path == "/api/venues":
            return EventType.VENUE_VIEW.value
        elif path == "/api/content":
            return EventType.CONTENT_VIEW.value
        elif path == "/api/content/stories":
            return EventType.STORY_VIEW.value
        elif "/venues/" in path:
            return EventType.VENUE_VIEW.value
        elif "/content/" in path:
            return EventType.CONTENT_VIEW.value
        elif path == "/" or path == "/public":
            return EventType.SESSION_START.value
        
        return None

class AnalyticsTracker:
    """Helper class for manual analytics tracking"""
    
    @staticmethod
    def track_search(search_term: str, search_type: str = None, results_count: int = 0):
        """Track search events"""
        analytics_db.track_search(search_term, search_type, results_count)
    
    @staticmethod
    def track_share(venue_id: int = None, content_id: int = None, platform: str = None, 
                   session_id: str = None, ip_address: str = None):
        """Track share events"""
        event = AnalyticsEvent(
            event_type=EventType.SHARE.value,
            venue_id=venue_id,
            content_id=content_id,
            user_session=session_id,
            ip_address=ip_address,
            properties={"platform": platform}
        )
        analytics_db.track_event(event)
    
    @staticmethod
    def track_favorite(venue_id: int = None, content_id: int = None, 
                      session_id: str = None, ip_address: str = None):
        """Track favorite events"""
        event = AnalyticsEvent(
            event_type=EventType.FAVORITE.value,
            venue_id=venue_id,
            content_id=content_id,
            user_session=session_id,
            ip_address=ip_address
        )
        analytics_db.track_event(event)
    
    @staticmethod
    def track_click(element: str, venue_id: int = None, content_id: int = None,
                   session_id: str = None, ip_address: str = None):
        """Track click events"""
        event = AnalyticsEvent(
            event_type=EventType.CLICK.value,
            venue_id=venue_id,
            content_id=content_id,
            user_session=session_id,
            ip_address=ip_address,
            properties={"element": element}
        )
        analytics_db.track_event(event)
    
    @staticmethod
    def track_filter(filter_type: str, filter_value: str, results_count: int = 0,
                    session_id: str = None, ip_address: str = None):
        """Track filter usage"""
        event = AnalyticsEvent(
            event_type=EventType.FILTER.value,
            user_session=session_id,
            ip_address=ip_address,
            properties={
                "filter_type": filter_type,
                "filter_value": filter_value,
                "results_count": results_count
            }
        )
        analytics_db.track_event(event)
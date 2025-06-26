import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import json
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    VENUE_VIEW = "venue_view"
    CONTENT_VIEW = "content_view" 
    STORY_VIEW = "story_view"
    SEARCH = "search"
    FILTER = "filter"
    SHARE = "share"
    FAVORITE = "favorite"
    CLICK = "click"
    SESSION_START = "session_start"
    SESSION_END = "session_end"

@dataclass
class AnalyticsEvent:
    event_type: str
    venue_id: Optional[int] = None
    content_id: Optional[int] = None
    user_session: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    properties: Optional[Dict] = None
    timestamp: Optional[datetime] = None

class AnalyticsDatabase:
    def __init__(self, db_path: str = "nightlife.db"):
        self.db_path = db_path
        self.init_analytics_tables()
    
    def init_analytics_tables(self):
        """Initialize analytics-specific database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Analytics events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    venue_id INTEGER,
                    content_id INTEGER,
                    user_session TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    properties TEXT, -- JSON string
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (venue_id) REFERENCES venues (id),
                    FOREIGN KEY (content_id) REFERENCES content (id)
                )
            ''')
            
            # User sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    page_views INTEGER DEFAULT 0,
                    duration INTEGER DEFAULT 0, -- seconds
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Daily venue stats
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_venue_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venue_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    views INTEGER DEFAULT 0,
                    unique_visitors INTEGER DEFAULT 0,
                    content_views INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    favorites INTEGER DEFAULT 0,
                    UNIQUE(venue_id, date),
                    FOREIGN KEY (venue_id) REFERENCES venues (id)
                )
            ''')
            
            # Daily content stats
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_content_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id INTEGER NOT NULL,
                    venue_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    views INTEGER DEFAULT 0,
                    unique_visitors INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    engagement_time INTEGER DEFAULT 0, -- seconds
                    UNIQUE(content_id, date),
                    FOREIGN KEY (content_id) REFERENCES content (id),
                    FOREIGN KEY (venue_id) REFERENCES venues (id)
                )
            ''')
            
            # Popular searches
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_term TEXT NOT NULL,
                    search_type TEXT, -- venue, neighborhood, content
                    results_count INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Geographic analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS geographic_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT,
                    estimated_location TEXT, -- city, country
                    venue_id INTEGER,
                    date DATE DEFAULT (date('now')),
                    views INTEGER DEFAULT 1,
                    FOREIGN KEY (venue_id) REFERENCES venues (id)
                )
            ''')
            
            # Performance metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metadata TEXT, -- JSON string
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON analytics_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_events_venue ON analytics_events(venue_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_events_content ON analytics_events(content_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_venue_stats_date ON daily_venue_stats(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_content_stats_date ON daily_content_stats(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_session ON user_sessions(session_id)')
            
            conn.commit()
    
    def track_event(self, event: AnalyticsEvent):
        """Track an analytics event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            properties_json = json.dumps(event.properties) if event.properties else None
            
            cursor.execute('''
                INSERT INTO analytics_events 
                (event_type, venue_id, content_id, user_session, ip_address, 
                 user_agent, referrer, properties, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_type, event.venue_id, event.content_id,
                event.user_session, event.ip_address, event.user_agent,
                event.referrer, properties_json, event.timestamp or datetime.now()
            ))
            
            conn.commit()
            
            # Update daily stats
            self._update_daily_stats(event)
    
    def _update_daily_stats(self, event: AnalyticsEvent):
        """Update daily aggregated statistics"""
        today = datetime.now().date()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if event.venue_id and event.event_type == EventType.VENUE_VIEW.value:
                cursor.execute('''
                    INSERT INTO daily_venue_stats (venue_id, date, views, unique_visitors)
                    VALUES (?, ?, 1, 1)
                    ON CONFLICT(venue_id, date) DO UPDATE SET
                    views = views + 1,
                    unique_visitors = unique_visitors + 
                        CASE WHEN NOT EXISTS (
                            SELECT 1 FROM analytics_events 
                            WHERE venue_id = ? AND event_type = ? 
                            AND date(timestamp) = ? AND user_session = ?
                            AND id != (SELECT max(id) FROM analytics_events)
                        ) THEN 1 ELSE 0 END
                ''', (event.venue_id, today, event.venue_id, event.event_type, 
                      today, event.user_session))
            
            if event.content_id and event.event_type == EventType.CONTENT_VIEW.value:
                # Get venue_id for content
                cursor.execute('SELECT venue_id FROM content WHERE id = ?', (event.content_id,))
                venue_result = cursor.fetchone()
                if venue_result:
                    venue_id = venue_result[0]
                    cursor.execute('''
                        INSERT INTO daily_content_stats (content_id, venue_id, date, views, unique_visitors)
                        VALUES (?, ?, ?, 1, 1)
                        ON CONFLICT(content_id, date) DO UPDATE SET
                        views = views + 1,
                        unique_visitors = unique_visitors + 
                            CASE WHEN NOT EXISTS (
                                SELECT 1 FROM analytics_events 
                                WHERE content_id = ? AND event_type = ? 
                                AND date(timestamp) = ? AND user_session = ?
                                AND id != (SELECT max(id) FROM analytics_events)
                            ) THEN 1 ELSE 0 END
                    ''', (event.content_id, venue_id, today, event.content_id, 
                          event.event_type, today, event.user_session))
            
            conn.commit()
    
    def start_session(self, session_id: str, ip_address: str, user_agent: str, referrer: str = None):
        """Start a new user session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_sessions 
                (session_id, ip_address, user_agent, referrer, start_time, last_activity)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (session_id, ip_address, user_agent, referrer))
            conn.commit()
    
    def update_session(self, session_id: str):
        """Update session last activity"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_sessions 
                SET last_activity = CURRENT_TIMESTAMP,
                    page_views = page_views + 1,
                    duration = CAST((julianday(CURRENT_TIMESTAMP) - julianday(start_time)) * 86400 AS INTEGER)
                WHERE session_id = ?
            ''', (session_id,))
            conn.commit()
    
    def get_venue_analytics(self, venue_id: int, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a specific venue"""
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Basic stats
            cursor.execute('''
                SELECT 
                    SUM(views) as total_views,
                    SUM(unique_visitors) as unique_visitors,
                    SUM(content_views) as content_views,
                    SUM(shares) as shares,
                    SUM(favorites) as favorites
                FROM daily_venue_stats 
                WHERE venue_id = ? AND date >= ?
            ''', (venue_id, start_date))
            
            stats = dict(cursor.fetchone() or {})
            
            # Daily breakdown
            cursor.execute('''
                SELECT date, views, unique_visitors, content_views
                FROM daily_venue_stats 
                WHERE venue_id = ? AND date >= ?
                ORDER BY date
            ''', (venue_id, start_date))
            
            daily_stats = [dict(row) for row in cursor.fetchall()]
            
            # Top content
            cursor.execute('''
                SELECT c.id, c.caption, c.content_type, SUM(dcs.views) as views
                FROM content c
                JOIN daily_content_stats dcs ON c.id = dcs.content_id
                WHERE c.venue_id = ? AND dcs.date >= ?
                GROUP BY c.id
                ORDER BY views DESC
                LIMIT 10
            ''', (venue_id, start_date))
            
            top_content = [dict(row) for row in cursor.fetchall()]
            
            return {
                'venue_id': venue_id,
                'period_days': days,
                'stats': stats,
                'daily_breakdown': daily_stats,
                'top_content': top_content
            }
    
    def get_content_analytics(self, content_id: int) -> Dict[str, Any]:
        """Get analytics for specific content"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Content stats
            cursor.execute('''
                SELECT 
                    SUM(views) as total_views,
                    SUM(unique_visitors) as unique_visitors,
                    SUM(shares) as shares,
                    AVG(engagement_time) as avg_engagement_time
                FROM daily_content_stats 
                WHERE content_id = ?
            ''', (content_id,))
            
            stats = dict(cursor.fetchone() or {})
            
            # Daily breakdown
            cursor.execute('''
                SELECT date, views, unique_visitors, shares, engagement_time
                FROM daily_content_stats 
                WHERE content_id = ?
                ORDER BY date DESC
                LIMIT 30
            ''', (content_id,))
            
            daily_stats = [dict(row) for row in cursor.fetchall()]
            
            return {
                'content_id': content_id,
                'stats': stats,
                'daily_breakdown': daily_stats
            }
    
    def get_global_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get global platform analytics"""
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Overall stats
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT user_session) as unique_visitors,
                    COUNT(*) as total_events,
                    COUNT(CASE WHEN event_type = 'venue_view' THEN 1 END) as venue_views,
                    COUNT(CASE WHEN event_type = 'content_view' THEN 1 END) as content_views
                FROM analytics_events 
                WHERE date(timestamp) >= ?
            ''', (start_date,))
            
            global_stats = dict(cursor.fetchone())
            
            # Top venues
            cursor.execute('''
                SELECT v.name, v.neighborhood, SUM(dvs.views) as views
                FROM venues v
                JOIN daily_venue_stats dvs ON v.id = dvs.venue_id
                WHERE dvs.date >= ?
                GROUP BY v.id
                ORDER BY views DESC
                LIMIT 10
            ''', (start_date,))
            
            top_venues = [dict(row) for row in cursor.fetchall()]
            
            # Popular searches
            cursor.execute('''
                SELECT search_term, COUNT(*) as frequency
                FROM search_analytics
                WHERE date(timestamp) >= ?
                GROUP BY search_term
                ORDER BY frequency DESC
                LIMIT 20
            ''', (start_date,))
            
            popular_searches = [dict(row) for row in cursor.fetchall()]
            
            # Daily activity
            cursor.execute('''
                SELECT 
                    date(timestamp) as date,
                    COUNT(DISTINCT user_session) as unique_visitors,
                    COUNT(*) as total_events
                FROM analytics_events 
                WHERE date(timestamp) >= ?
                GROUP BY date(timestamp)
                ORDER BY date
            ''', (start_date,))
            
            daily_activity = [dict(row) for row in cursor.fetchall()]
            
            return {
                'period_days': days,
                'global_stats': global_stats,
                'top_venues': top_venues,
                'popular_searches': popular_searches,
                'daily_activity': daily_activity
            }
    
    def track_search(self, search_term: str, search_type: str = None, results_count: int = 0):
        """Track search queries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO search_analytics (search_term, search_type, results_count)
                VALUES (?, ?, ?)
            ''', (search_term.lower().strip(), search_type, results_count))
            conn.commit()
    
    def get_performance_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent performance metrics"""
        start_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT metric_name, metric_value, metadata, timestamp
                FROM performance_metrics
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (start_time,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def record_performance_metric(self, metric_name: str, value: float, metadata: Dict = None):
        """Record a performance metric"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            metadata_json = json.dumps(metadata) if metadata else None
            cursor.execute('''
                INSERT INTO performance_metrics (metric_name, metric_value, metadata)
                VALUES (?, ?, ?)
            ''', (metric_name, value, metadata_json))
            conn.commit()

# Initialize global analytics database
analytics_db = AnalyticsDatabase()
# NYC Nightlife API - Analytics Features

## Overview

The NYC Nightlife API now includes comprehensive analytics capabilities to track user behavior, venue performance, content engagement, and platform usage. All analytics data is automatically collected, processed, and made available through secure admin endpoints.

## Analytics Features

### 🔍 **Automatic Data Collection**
- **User Sessions**: Session tracking with duration and page views
- **Event Tracking**: Automatic tracking of venue views, content views, searches
- **Performance Metrics**: Response time monitoring and API performance
- **Geographic Data**: IP-based location insights (privacy-compliant)

### 📊 **Real-time Analytics**
- **Live Sessions**: Active users in last 30 minutes
- **Trending Content**: Most viewed venues and content in real-time
- **Recent Activity**: Live event stream and search terms
- **Performance Monitoring**: API response times and errors

### 📈 **Historical Analytics**
- **Venue Performance**: Views, unique visitors, engagement over time
- **Content Analytics**: Individual content piece performance
- **Platform Metrics**: Overall platform usage trends
- **Search Analytics**: Popular search terms and patterns

### 📋 **Admin Dashboard**
- **Interactive Charts**: Canvas-based activity visualizations
- **Real-time Stats**: Auto-refreshing dashboard every 30 seconds
- **Venue Rankings**: Top performing venues with detailed metrics
- **Export Tools**: CSV export for external analysis

## Database Schema

### Core Analytics Tables

```sql
-- Event tracking
analytics_events (
    id, event_type, venue_id, content_id, user_session,
    ip_address, user_agent, referrer, properties, timestamp
)

-- User sessions
user_sessions (
    id, session_id, ip_address, user_agent, referrer,
    start_time, last_activity, page_views, duration, is_active
)

-- Aggregated daily stats
daily_venue_stats (
    id, venue_id, date, views, unique_visitors, 
    content_views, shares, favorites
)

daily_content_stats (
    id, content_id, venue_id, date, views, 
    unique_visitors, shares, engagement_time
)

-- Search analytics
search_analytics (
    id, search_term, search_type, results_count, timestamp
)

-- Performance metrics
performance_metrics (
    id, metric_name, metric_value, metadata, timestamp
)
```

## API Endpoints

### Admin Analytics Endpoints (Authentication Required)

```
GET  /api/admin/analytics/global?days=30
GET  /api/admin/analytics/venues/{venue_id}?days=30
GET  /api/admin/analytics/content/{content_id}
GET  /api/admin/analytics/performance?hours=24
GET  /api/admin/analytics/realtime
POST /api/admin/analytics/export
```

### Public Tracking Endpoints (Rate Limited)

```
POST /api/track/search      - Track search queries
POST /api/track/share       - Track share events
POST /api/track/favorite    - Track favorite actions
```

## Event Types Tracked

### Automatic Events
- `venue_view` - User views venue list or specific venue
- `content_view` - User views content items
- `story_view` - User views Instagram stories
- `session_start` - User starts browsing session
- `session_end` - User session expires

### Manual Events (via tracking endpoints)
- `search` - User searches for venues/content
- `share` - User shares venue/content
- `favorite` - User favorites venue/content
- `click` - User clicks specific elements
- `filter` - User applies filters

## Analytics Dashboard Features

### Real-time Overview
- Active sessions (last 30 minutes)
- Recent events (last hour)
- Trending venues and content
- Live search terms

### Platform Analytics
- Unique visitors by time period
- Total venue and content views
- Event count and engagement metrics
- Popular search terms with frequency

### Venue Performance
- Ranking table with views and engagement
- Individual venue detailed analytics
- Content performance per venue
- Trend analysis over time

### Export Capabilities
- CSV export for venues, events, and sessions
- Date range selection
- Filtered exports by venue
- Audit trail of export actions

## Usage Examples

### Track Custom Events (JavaScript)
```javascript
// Track search
fetch('/api/track/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        search_term: 'rooftop bars',
        search_type: 'venue',
        results_count: 15
    })
});

// Track share
fetch('/api/track/share', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        venue_id: 123,
        platform: 'twitter'
    })
});
```

### Admin Analytics Access
```javascript
// Get venue analytics
const response = await fetch('/api/admin/analytics/venues/123?days=30', {
    headers: { 'Authorization': `Bearer ${token}` }
});
const analytics = await response.json();

// Export data
const exportResponse = await fetch('/api/admin/analytics/export', {
    method: 'POST',
    headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        export_type: 'venues',
        start_date: '2024-01-01',
        end_date: '2024-01-31'
    })
});
```

## Analytics Data Structure

### Global Analytics Response
```json
{
    "period_days": 30,
    "global_stats": {
        "unique_visitors": 1250,
        "total_events": 8750,
        "venue_views": 3200,
        "content_views": 4100
    },
    "top_venues": [
        {"name": "Sky Lounge", "neighborhood": "Manhattan", "views": 450}
    ],
    "popular_searches": [
        {"search_term": "rooftop", "frequency": 89}
    ],
    "daily_activity": [
        {"date": "2024-01-01", "unique_visitors": 45, "total_events": 320}
    ]
}
```

### Venue Analytics Response
```json
{
    "venue_id": 123,
    "period_days": 30,
    "stats": {
        "total_views": 450,
        "unique_visitors": 320,
        "content_views": 180,
        "shares": 25,
        "favorites": 67
    },
    "daily_breakdown": [
        {"date": "2024-01-01", "views": 15, "unique_visitors": 12}
    ],
    "top_content": [
        {"id": 456, "caption": "Amazing night!", "content_type": "post", "views": 89}
    ]
}
```

## Privacy & Compliance

### Data Collection
- **Session IDs**: UUID-based, no personal identification
- **IP Addresses**: Stored for analytics, can be anonymized
- **User Agents**: Browser information for analytics only
- **No Personal Data**: No emails, names, or identifying information

### Data Retention
- **Raw Events**: Configurable retention period
- **Aggregated Data**: Permanent for historical analysis
- **Session Data**: Automatic cleanup of inactive sessions
- **Export Logs**: Maintained for audit compliance

### GDPR Compliance
- Analytics data is aggregated and anonymized
- No tracking cookies used (session-based only)
- Data export capabilities for compliance requests
- Clear audit trail of all data access

## Performance Considerations

### Optimizations
- **Database Indexing**: Optimized queries for analytics performance
- **Aggregated Tables**: Pre-computed daily/weekly stats
- **Rate Limiting**: Public endpoints protected against abuse
- **Async Processing**: Non-blocking analytics collection

### Monitoring
- **Response Times**: Tracked per endpoint
- **Error Rates**: Monitored for API health
- **Database Performance**: Query optimization metrics
- **Memory Usage**: Analytics processing overhead

## Configuration

### Environment Variables
```env
# Analytics settings
ANALYTICS_ENABLED=true
ANALYTICS_RETENTION_DAYS=365
ANALYTICS_BATCH_SIZE=1000
ANALYTICS_EXPORT_LIMIT=50000
```

### Database Maintenance
```sql
-- Clean old events (run daily)
DELETE FROM analytics_events 
WHERE timestamp < date('now', '-365 days');

-- Update aggregated stats (run nightly)
INSERT OR REPLACE INTO daily_venue_stats ...
```

## Integration with AI/ML

### Data Preparation
- **Structured Data**: Ready for ML model training
- **Feature Engineering**: Pre-computed engagement metrics
- **Time Series**: Historical data for trend prediction
- **Export Formats**: CSV/JSON for ML pipelines

### Use Cases
- **Recommendation Engine**: Popular venues by time/location
- **Trend Prediction**: Venue popularity forecasting
- **Content Optimization**: Best performing content analysis
- **User Segmentation**: Behavioral pattern analysis

## Troubleshooting

### Common Issues
1. **Missing Analytics Data**: Check middleware configuration
2. **Slow Dashboard**: Verify database indexes
3. **Export Failures**: Check date formats and permissions
4. **Real-time Updates**: Confirm WebSocket/polling setup

### Debug Endpoints
```
GET /api/admin/analytics/performance  - Check system performance
GET /api/admin/audit-log             - View admin actions
```

## Future Enhancements

### Planned Features
- **A/B Testing Framework**: Content performance comparison
- **Cohort Analysis**: User retention tracking
- **Predictive Analytics**: ML-powered insights
- **Custom Dashboards**: Configurable admin views
- **API Integration**: Third-party analytics tools
- **Mobile Analytics**: App-specific tracking

The analytics system provides comprehensive insights into your NYC nightlife platform while maintaining user privacy and security standards.
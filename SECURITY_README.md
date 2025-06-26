# NYC Nightlife API - Secure Version

## Security Improvements Summary

The NYC Nightlife API has been completely overhauled with enterprise-grade security features. **All user submission capabilities have been removed** - only administrators can now create and manage content.

## Key Security Features

### 🔐 Authentication & Authorization
- **JWT-based authentication** with access and refresh tokens
- **Admin-only access** to all content management endpoints
- **Role-based permissions** system ready for future expansion
- **Secure password hashing** using bcrypt

### 🛡️ Input Validation & Sanitization
- **Pydantic models** for strict input validation
- **File type restrictions** (only allowed image/video formats)
- **File size limits** (10MB maximum)
- **SQL injection protection** through parameterized queries

### 🌐 Network Security
- **Restricted CORS policy** - only allows specific origins
- **Rate limiting** to prevent abuse (100 requests/minute per IP)
- **Request throttling** on authentication endpoints

### 📝 Audit & Monitoring
- **Complete audit trail** of all admin actions
- **IP address logging** for security monitoring
- **Session management** with token expiration

## Architecture Changes

### Removed Features (Security)
- ❌ Public venue submission endpoint (`POST /venues`)
- ❌ Public content submission endpoint (`POST /content`)
- ❌ Open file uploads from anonymous users
- ❌ Unrestricted CORS (now limited to specific origins)

### New Admin-Only Features
- ✅ Secure admin authentication system
- ✅ Protected venue management (`POST/PUT/DELETE /api/admin/venues/*`)
- ✅ Protected content management (`POST/DELETE /api/admin/content/*`)
- ✅ Admin dashboard web interface
- ✅ Audit log viewing

### Public Read-Only Features (Maintained)
- ✅ View venues (`GET /api/venues`)
- ✅ View content (`GET /api/content`)
- ✅ View stories (`GET /api/content/stories`)
- ✅ Public interface remains unchanged

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# IMPORTANT: Change SECRET_KEY in production!
```

### 3. Initialize Database
```bash
# This will create the secure database schema
python database.py
```

### 4. Create First Admin User
```bash
python create_admin.py
```

### 5. Start Secure API Server
```bash
python secure_api_server.py
```

## API Endpoints

### Public Endpoints (No Authentication)
```
GET  /api/venues              - List all venues
GET  /api/content             - List all content  
GET  /api/content/stories     - List active stories
GET  /                        - Public interface
```

### Authentication Endpoints
```
POST /api/auth/login          - Admin login (rate limited: 5/min)
POST /api/auth/refresh        - Refresh access token
GET  /api/auth/me             - Get current user info
```

### Admin-Only Endpoints (Requires Authentication)
```
POST   /api/admin/venues      - Create venue
PUT    /api/admin/venues/{id} - Update venue  
DELETE /api/admin/venues/{id} - Delete venue
POST   /api/admin/content     - Create content
DELETE /api/admin/content/{id} - Delete content
GET    /api/admin/audit-log   - View audit log
```

### Admin Interface
```
GET /admin                    - Admin login page
GET /admin/dashboard          - Admin dashboard (requires auth)
```

## Admin Dashboard Features

- **Venue Management**: Add, edit, delete venues with validation
- **Content Management**: Upload and manage media content
- **Audit Log**: View all administrative actions
- **File Upload**: Secure file handling with type/size validation
- **Real-time Updates**: Dynamic interface updates

## Security Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
MAX_UPLOAD_SIZE=10485760  # 10MB
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### File Upload Security
- **Allowed types**: .jpg, .jpeg, .png, .gif, .mp4, .mov
- **Size limit**: 10MB maximum
- **Secure naming**: UUID-based filenames prevent conflicts
- **Validation**: File type and size checked before storage

### Rate Limiting
- **General API**: 30 requests/minute per IP
- **Auth endpoints**: 5 requests/minute per IP
- **Protection**: Prevents brute force and abuse

## Database Schema

### New Security Tables
```sql
admin_users     - Administrator accounts
api_keys        - API key management (future use)
audit_log       - Complete action audit trail
```

### Enhanced Existing Tables
```sql
venues          - Added created_by, updated_at
content         - Added created_by, updated_at
```

## Deployment Recommendations

### Production Security
1. **Change SECRET_KEY** to a strong, unique value
2. **Use HTTPS** for all communications
3. **Restrict ALLOWED_ORIGINS** to your actual domains
4. **Set up reverse proxy** (nginx) for additional security
5. **Enable database backups** with encryption
6. **Monitor audit logs** regularly
7. **Use environment-specific settings**

### Server Configuration
```bash
# Production example with gunicorn
gunicorn secure_api_server:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Migration from Previous Version

1. **Backup existing database**
2. **Run secure database initialization**
3. **Create admin users**
4. **Update any client applications** to use new API endpoints
5. **Test authentication flow**
6. **Remove old insecure API server**

## Future AI/ML Integration

The secure API is prepared for Instagram API integration and AI/ML features:

- **Admin endpoints** ready for automated content ingestion
- **Audit system** will track AI/ML actions
- **Flexible content schema** supports additional metadata
- **Secure file storage** for processed media
- **API key system** ready for service-to-service authentication

## Support

For issues with the secure implementation, check:
1. **Authentication flow** - Ensure tokens are properly stored/sent
2. **CORS configuration** - Verify allowed origins match your setup
3. **File uploads** - Check file types and sizes meet requirements
4. **Rate limits** - Monitor for limit exceeded errors

## Security Audit Checklist

- [x] Authentication required for all write operations
- [x] Input validation on all endpoints
- [x] File upload restrictions enforced
- [x] Rate limiting implemented
- [x] CORS properly configured
- [x] Audit logging in place
- [x] SQL injection protection
- [x] Session management secure
- [x] Password hashing implemented
- [x] Error handling doesn't leak sensitive info
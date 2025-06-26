#!/bin/bash
# Atlas-NYC Production Deployment Script

set -e  # Exit on error

echo "🚀 Atlas-NYC Production Deployment Starting..."

# Configuration
APP_NAME="atlas-nyc"
DEPLOY_DIR="/var/www/atlas-nyc"
BACKUP_DIR="/var/backups/atlas-nyc"
LOG_FILE="/var/log/atlas-nyc-deploy.log"
PYTHON_VERSION="3.11"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# Success message
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Warning message
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running as appropriate user
check_user() {
    if [ "$EUID" -eq 0 ]; then 
        error_exit "Do not run as root. Use sudo for specific commands."
    fi
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check Python version
    if ! command -v python$PYTHON_VERSION &> /dev/null; then
        error_exit "Python $PYTHON_VERSION is not installed"
    fi
    
    # Check required services
    for service in nginx postgresql redis; do
        if ! systemctl is-active --quiet $service; then
            warning "$service is not running"
        fi
    done
    
    # Check disk space
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 80 ]; then
        warning "Disk usage is above 80%"
    fi
    
    success "Pre-deployment checks completed"
}

# Backup current deployment
backup_current() {
    log "Creating backup of current deployment..."
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/$TIMESTAMP"
    
    mkdir -p "$BACKUP_PATH"
    
    # Backup database
    if [ -f "$DEPLOY_DIR/nightlife.db" ]; then
        cp "$DEPLOY_DIR/nightlife.db" "$BACKUP_PATH/nightlife.db"
        success "Database backed up"
    fi
    
    # Backup uploads
    if [ -d "$DEPLOY_DIR/uploads" ]; then
        cp -r "$DEPLOY_DIR/uploads" "$BACKUP_PATH/uploads"
        success "Uploads backed up"
    fi
    
    # Backup environment file
    if [ -f "$DEPLOY_DIR/.env" ]; then
        cp "$DEPLOY_DIR/.env" "$BACKUP_PATH/.env"
        success "Environment file backed up"
    fi
}

# Deploy new code
deploy_code() {
    log "Deploying new code..."
    
    # Create deployment directory
    sudo mkdir -p "$DEPLOY_DIR"
    sudo chown $USER:$USER "$DEPLOY_DIR"
    
    # Copy application files
    rsync -av --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
          --exclude='.git' --exclude='logs/*' --exclude='uploads/*' \
          ./ "$DEPLOY_DIR/"
    
    success "Code deployed"
}

# Setup Python environment
setup_python_env() {
    log "Setting up Python environment..."
    
    cd "$DEPLOY_DIR"
    
    # Create virtual environment
    python$PYTHON_VERSION -m venv venv
    
    # Activate and upgrade pip
    source venv/bin/activate
    pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    
    success "Python environment ready"
}

# Setup production configuration
setup_production_config() {
    log "Setting up production configuration..."
    
    # Check for .env file
    if [ ! -f "$DEPLOY_DIR/.env" ]; then
        warning ".env file not found. Creating from template..."
        
        cat > "$DEPLOY_DIR/.env" << EOF
# Atlas-NYC Production Configuration
# CRITICAL: Update all values before running!

# Security
SECRET_KEY=CHANGE_THIS_TO_SECURE_RANDOM_KEY
ALGORITHM=HS256

# Environment
ENVIRONMENT=production
DEBUG=false

# Domain
BASE_URL=https://atlas-nyc.com
ALLOWED_ORIGINS=["https://atlas-nyc.com","https://www.atlas-nyc.com"]

# Database (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@localhost/atlasnyc

# Google Maps
GOOGLE_MAPS_API_KEY=your_api_key_here

# SSL
SSL_CERT_PATH=/etc/letsencrypt/live/atlas-nyc.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/atlas-nyc.com/privkey.pem

# Redis
REDIS_URL=redis://localhost:6379

# Monitoring (optional)
SENTRY_DSN=
EOF
        
        chmod 600 "$DEPLOY_DIR/.env"
        error_exit "Please update .env file with production values and run again"
    fi
    
    success "Production configuration ready"
}

# Initialize database
initialize_database() {
    log "Initializing database..."
    
    cd "$DEPLOY_DIR"
    source venv/bin/activate
    
    # Run database initialization
    python init_database.py
    
    # Run optimization
    python optimize_database.py
    
    success "Database initialized"
}

# Setup nginx
setup_nginx() {
    log "Setting up nginx..."
    
    # Create nginx configuration
    sudo tee /etc/nginx/sites-available/atlas-nyc << EOF
server {
    listen 80;
    server_name atlas-nyc.com www.atlas-nyc.com;
    
    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name atlas-nyc.com www.atlas-nyc.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/atlas-nyc.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/atlas-nyc.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Uploads
    client_max_body_size 10M;
    
    # Static files
    location /static {
        alias $DEPLOY_DIR/static;
        expires 30d;
    }
    
    location /uploads {
        alias $DEPLOY_DIR/uploads;
        expires 7d;
    }
    
    # API proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/atlas-nyc /etc/nginx/sites-enabled/
    
    # Test configuration
    sudo nginx -t || error_exit "Nginx configuration test failed"
    
    # Reload nginx
    sudo systemctl reload nginx
    
    success "Nginx configured"
}

# Setup systemd service
setup_systemd() {
    log "Setting up systemd service..."
    
    sudo tee /etc/systemd/system/atlas-nyc.service << EOF
[Unit]
Description=Atlas-NYC API Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$DEPLOY_DIR
Environment="PATH=$DEPLOY_DIR/venv/bin"
ExecStart=$DEPLOY_DIR/venv/bin/python start.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable and start service
    sudo systemctl enable atlas-nyc
    sudo systemctl restart atlas-nyc
    
    success "Systemd service configured"
}

# Run tests
run_tests() {
    log "Running tests..."
    
    cd "$DEPLOY_DIR"
    source venv/bin/activate
    
    # Run pytest
    pytest test_api.py -v || warning "Some tests failed"
    
    success "Tests completed"
}

# Post-deployment checks
post_deployment_checks() {
    log "Running post-deployment checks..."
    
    # Check service status
    if ! systemctl is-active --quiet atlas-nyc; then
        error_exit "Atlas-NYC service is not running"
    fi
    
    # Check API health
    sleep 5
    HEALTH_CHECK=$(curl -s http://localhost:8000/health | grep -c "healthy" || true)
    if [ "$HEALTH_CHECK" -eq 0 ]; then
        error_exit "Health check failed"
    fi
    
    success "Post-deployment checks passed"
}

# Main deployment flow
main() {
    log "=== Atlas-NYC Production Deployment ==="
    
    check_user
    pre_deployment_checks
    backup_current
    deploy_code
    setup_python_env
    setup_production_config
    initialize_database
    setup_nginx
    setup_systemd
    run_tests
    post_deployment_checks
    
    echo ""
    success "Deployment completed successfully! 🎉"
    log "Deployment finished"
    
    echo ""
    echo "Next steps:"
    echo "1. Update .env with production values"
    echo "2. Set up SSL certificates with Let's Encrypt"
    echo "3. Configure monitoring and alerts"
    echo "4. Set up automated backups"
    echo "5. Monitor logs: sudo journalctl -u atlas-nyc -f"
}

# Run main function
main "$@"
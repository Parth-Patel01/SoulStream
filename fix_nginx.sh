#!/bin/bash

# SoulStream Nginx Configuration Fix Script
# This script fixes the Nginx configuration syntax error

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo -e "${BLUE}🔧 Fixing Nginx Configuration${NC}"
echo "================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Backup existing configuration
print_status "Backing up existing Nginx configuration..."
if [ -f /etc/nginx/sites-available/soulstream ]; then
    cp /etc/nginx/sites-available/soulstream /etc/nginx/sites-available/soulstream.backup.$(date +%Y%m%d_%H%M%S)
    print_status "Backup created"
fi

# Create correct Nginx configuration
print_status "Creating correct Nginx configuration..."
cat > /etc/nginx/sites-available/soulstream << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # For large file uploads
        client_max_body_size 16G;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

print_status "Nginx configuration created"

# Test Nginx configuration
print_status "Testing Nginx configuration..."
if nginx -t; then
    print_status "✅ Nginx configuration is valid"
else
    print_error "❌ Nginx configuration test failed"
    exit 1
fi

# Restart Nginx
print_status "Restarting Nginx..."
if systemctl restart nginx; then
    print_status "✅ Nginx restarted successfully"
else
    print_error "❌ Failed to restart Nginx"
    exit 1
fi

# Check Nginx status
print_status "Checking Nginx status..."
if systemctl is-active --quiet nginx; then
    print_status "✅ Nginx is running"
else
    print_error "❌ Nginx is not running"
    systemctl status nginx --no-pager -l
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Nginx configuration fixed successfully!${NC}"
echo "=========================================="
echo ""
echo "🌐 Your SoulStream server should now be accessible at:"
echo "   http://$(hostname -I | awk '{print $1}')"
echo ""
echo "📋 Useful commands:"
echo "  • Check Nginx status: systemctl status nginx"
echo "  • View Nginx logs: journalctl -u nginx -f"
echo "  • Test configuration: nginx -t"
echo "" 
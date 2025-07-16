#!/bin/bash

# SoulStream Nginx Debug and Fix Script
# This script will diagnose and fix Nginx configuration issues

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

echo -e "${BLUE}🔍 Nginx Debug and Fix Script${NC}"
echo "=================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Check current Nginx status
print_status "Checking Nginx status..."
systemctl status nginx --no-pager -l

echo ""
print_status "Current Nginx configuration files:"
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/sites-enabled/

echo ""
print_status "Content of soulstream configuration:"
if [ -f /etc/nginx/sites-available/soulstream ]; then
    cat /etc/nginx/sites-available/soulstream
else
    print_error "Soulstream configuration file not found!"
fi

echo ""
print_status "Testing Nginx configuration..."
nginx -t

echo ""
print_status "Checking for syntax errors in all config files..."
find /etc/nginx -name "*.conf" -exec echo "Checking {}" \; -exec nginx -t -c {} \;

echo ""
print_status "Checking for port conflicts..."
netstat -tlnp | grep :80
netstat -tlnp | grep :8080

echo ""
print_status "Checking Nginx error logs..."
tail -20 /var/log/nginx/error.log

echo ""
print_status "Creating a completely new, clean configuration..."

# Remove any existing soulstream config
rm -f /etc/nginx/sites-available/soulstream
rm -f /etc/nginx/sites-enabled/soulstream

# Create a minimal, working configuration
cat > /etc/nginx/sites-available/soulstream << 'EOF'
server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        client_max_body_size 16G;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

print_status "New configuration created"

# Test the new configuration
print_status "Testing new configuration..."
if nginx -t; then
    print_status "✅ Configuration test passed"
else
    print_error "❌ Configuration test failed"
    exit 1
fi

# Restart Nginx
print_status "Restarting Nginx..."
systemctl restart nginx

# Check if Nginx is running
print_status "Checking if Nginx is running..."
if systemctl is-active --quiet nginx; then
    print_status "✅ Nginx is running successfully"
else
    print_error "❌ Nginx failed to start"
    systemctl status nginx --no-pager -l
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Nginx should now be working!${NC}"
echo "=================================="
echo ""
echo "🌐 Test your server at:"
echo "   http://$(hostname -I | awk '{print $1}')"
echo ""
echo "📋 If you still have issues, check:"
echo "   • sudo journalctl -u nginx -f"
echo "   • sudo nginx -t"
echo "   • sudo systemctl status nginx"
echo "" 
#!/bin/bash

# SoulStream Media Server Installation Script for Raspberry Pi
# This script sets up the complete media server environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MEDIA_DIR="/media/soulstream"
SERVICE_NAME="soulstream"
SERVICE_USER="soulstream"
PORT=8080

echo -e "${BLUE}🎬 SoulStream Media Server Installation${NC}"
echo "=========================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install required system packages
print_status "Installing system dependencies..."
apt install -y python3 python3-pip python3-venv nginx git curl wget

# Create service user
print_status "Creating service user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d /home/$SERVICE_USER -m $SERVICE_USER
    print_status "Created user: $SERVICE_USER"
else
    print_status "User $SERVICE_USER already exists"
fi

# Create media directory
print_status "Setting up media directory..."
mkdir -p $MEDIA_DIR
chown $SERVICE_USER:$SERVICE_USER $MEDIA_DIR
chmod 755 $MEDIA_DIR
print_status "Media directory created: $MEDIA_DIR"

# Create application directory
APP_DIR="/opt/soulstream"
print_status "Setting up application directory..."
mkdir -p $APP_DIR
chown $SERVICE_USER:$SERVICE_USER $APP_DIR

# Copy application files
print_status "Copying application files..."
cp server.py $APP_DIR/
cp requirements.txt $APP_DIR/
cp index.html $APP_DIR/
cp styles.css $APP_DIR/
cp script.js $APP_DIR/

# Set proper permissions
chown -R $SERVICE_USER:$SERVICE_USER $APP_DIR
chmod +x $APP_DIR/server.py

# Create Python virtual environment
print_status "Setting up Python virtual environment..."
cd $APP_DIR
sudo -u $SERVICE_USER python3 -m venv venv
sudo -u $SERVICE_USER $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u $SERVICE_USER $APP_DIR/venv/bin/pip install -r requirements.txt

# Create systemd service file
print_status "Creating systemd service..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=SoulStream Media Server
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/server.py --host 0.0.0.0 --port $PORT
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
print_status "Enabling and starting service..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

# Configure firewall
print_status "Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow $PORT/tcp
    print_status "Firewall rule added for port $PORT"
else
    print_warning "ufw not found, please manually configure firewall for port $PORT"
fi

# Create Nginx configuration for reverse proxy (optional)
print_status "Setting up Nginx reverse proxy..."
cat > /etc/nginx/sites-available/$SERVICE_NAME << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # For large file uploads
        client_max_body_size 16G;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Remove default site
systemctl restart nginx

# Create log directory
print_status "Setting up logging..."
mkdir -p /var/log/$SERVICE_NAME
chown $SERVICE_USER:$SERVICE_USER /var/log/$SERVICE_NAME

# Create a simple status script
cat > /usr/local/bin/soulstream-status << EOF
#!/bin/bash
echo "🎬 SoulStream Media Server Status"
echo "================================"
echo "Service Status:"
systemctl status $SERVICE_NAME --no-pager -l
echo ""
echo "Media Directory: $MEDIA_DIR"
echo "Files in directory:"
ls -la $MEDIA_DIR
echo ""
echo "Server URL: http://$(hostname -I | awk '{print $1}'):$PORT"
echo "Nginx URL: http://$(hostname -I | awk '{print $1}')"
EOF

chmod +x /usr/local/bin/soulstream-status

# Create backup script
print_status "Creating backup script..."
cat > /usr/local/bin/soulstream-backup << EOF
#!/bin/bash
BACKUP_DIR="/backup/soulstream"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="soulstream_backup_\$DATE.tar.gz"

mkdir -p \$BACKUP_DIR
tar -czf \$BACKUP_DIR/\$BACKUP_FILE -C /media soulstream
echo "Backup created: \$BACKUP_DIR/\$BACKUP_FILE"
EOF

chmod +x /usr/local/bin/soulstream-backup

# Create cleanup script
print_status "Creating cleanup script..."
cat > /usr/local/bin/soulstream-cleanup << EOF
#!/bin/bash
echo "🧹 SoulStream Cleanup Script"
echo "============================"
echo "This will remove all uploaded files. Are you sure? (y/N)"
read -r response
if [[ "\$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    rm -rf $MEDIA_DIR/*
    echo "All files removed from $MEDIA_DIR"
else
    echo "Cleanup cancelled"
fi
EOF

chmod +x /usr/local/bin/soulstream-cleanup

# Check service status
print_status "Checking service status..."
if systemctl is-active --quiet $SERVICE_NAME; then
    print_status "✅ Service is running successfully!"
else
    print_error "❌ Service failed to start. Check logs with: journalctl -u $SERVICE_NAME"
    exit 1
fi

# Display final information
echo ""
echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
echo "=========================================="
echo ""
echo "📁 Media Directory: $MEDIA_DIR"
echo "🌐 Server URL: http://$(hostname -I | awk '{print $1}'):$PORT"
echo "🌐 Nginx URL: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "📋 Useful commands:"
echo "  • Check status: soulstream-status"
echo "  • View logs: journalctl -u $SERVICE_NAME -f"
echo "  • Restart service: systemctl restart $SERVICE_NAME"
echo "  • Create backup: soulstream-backup"
echo "  • Cleanup files: soulstream-cleanup"
echo ""
echo "🔧 Configuration:"
echo "  • Service file: /etc/systemd/system/$SERVICE_NAME.service"
echo "  • Application: $APP_DIR"
echo "  • Logs: /var/log/$SERVICE_NAME"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo "  • Make sure your firewall allows port $PORT"
echo "  • The media directory is: $MEDIA_DIR"
echo "  • Files uploaded via web interface will be stored there"
echo "  • You can integrate this with Plex, Jellyfin, or other media servers"
echo ""
echo -e "${GREEN}🚀 Your SoulStream Media Server is ready!${NC}" 
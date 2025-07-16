# 🔧 Manual Nginx Fix Guide

If the automatic scripts don't work, follow these manual steps:

## Step 1: Check Current Status
```bash
sudo systemctl status nginx
sudo nginx -t
```

## Step 2: Backup and Remove Problematic Config
```bash
# Backup existing config
sudo cp /etc/nginx/sites-available/soulstream /etc/nginx/sites-available/soulstream.backup

# Remove the problematic config
sudo rm /etc/nginx/sites-available/soulstream
sudo rm /etc/nginx/sites-enabled/soulstream
```

## Step 3: Create New Configuration
```bash
sudo nano /etc/nginx/sites-available/soulstream
```

**Copy and paste this exact configuration:**
```nginx
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
```

## Step 4: Enable the Site
```bash
sudo ln -s /etc/nginx/sites-available/soulstream /etc/nginx/sites-enabled/
```

## Step 5: Test and Restart
```bash
# Test configuration
sudo nginx -t

# If test passes, restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

## Step 6: Verify
```bash
# Check if Nginx is running
sudo systemctl is-active nginx

# Test the website
curl http://localhost
```

## Alternative: Disable Nginx Temporarily
If you want to use the Flask server directly without Nginx:

```bash
# Stop Nginx
sudo systemctl stop nginx
sudo systemctl disable nginx

# Access your server directly at:
# http://192.168.18.20:8080
```

## Troubleshooting Commands
```bash
# View Nginx error logs
sudo tail -f /var/log/nginx/error.log

# View Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Check what's using port 80
sudo lsof -i :80

# Check what's using port 8080
sudo lsof -i :8080

# Restart everything
sudo systemctl restart nginx
sudo systemctl restart soulstream
``` 
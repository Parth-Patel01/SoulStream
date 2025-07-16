#!/usr/bin/env python3
"""
Configuration file for SoulStream Media Server
Modify these settings to customize your server
"""

import os

# Server Configuration
HOST = '0.0.0.0'  # Bind to all interfaces
PORT = 8080        # Server port

# Upload Configuration
UPLOAD_FOLDER = '/media/soulstream'  # Directory to store uploaded files
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm'
}

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'soulstream.log'

# Security Configuration
CORS_ORIGINS = ['*']  # Allow all origins (change for production)

# Performance Configuration
UPLOAD_TIMEOUT = 300  # 5 minutes
MAX_WORKERS = 4       # Number of worker threads

# Media Server Integration
# Set these paths for automatic integration with media servers
PLEX_LIBRARY_PATH = None  # e.g., '/media/soulstream'
JELLYFIN_LIBRARY_PATH = None  # e.g., '/media/soulstream'

# Backup Configuration
BACKUP_ENABLED = True
BACKUP_DIR = '/backup/soulstream'
BACKUP_RETENTION_DAYS = 30

# Notification Configuration
ENABLE_NOTIFICATIONS = False
NOTIFICATION_WEBHOOK = None  # Discord/Slack webhook URL

# Development Configuration
DEBUG = False
RELOAD_ON_CHANGE = False

def get_config():
    """Get configuration dictionary"""
    return {
        'host': HOST,
        'port': PORT,
        'upload_folder': UPLOAD_FOLDER,
        'max_content_length': MAX_CONTENT_LENGTH,
        'allowed_extensions': ALLOWED_EXTENSIONS,
        'log_level': LOG_LEVEL,
        'log_file': LOG_FILE,
        'cors_origins': CORS_ORIGINS,
        'upload_timeout': UPLOAD_TIMEOUT,
        'max_workers': MAX_WORKERS,
        'debug': DEBUG,
        'reload_on_change': RELOAD_ON_CHANGE
    }

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check if upload folder is writable
    if not os.access(UPLOAD_FOLDER, os.W_OK):
        errors.append(f"Upload folder {UPLOAD_FOLDER} is not writable")
    
    # Check if port is valid
    if not (1024 <= PORT <= 65535):
        errors.append(f"Port {PORT} is not valid (must be between 1024-65535)")
    
    # Check if max content length is reasonable
    if MAX_CONTENT_LENGTH < 1024 * 1024:  # 1MB
        errors.append("MAX_CONTENT_LENGTH is too small")
    
    return errors

if __name__ == "__main__":
    # Print current configuration
    print("🎬 SoulStream Configuration")
    print("=" * 30)
    config = get_config()
    for key, value in config.items():
        print(f"{key}: {value}")
    
    # Validate configuration
    errors = validate_config()
    if errors:
        print("\n⚠️  Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ Configuration is valid") 
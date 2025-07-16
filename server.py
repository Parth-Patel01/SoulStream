#!/usr/bin/env python3
"""
SoulStream Media Server
A Flask-based server for uploading and serving media files
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import threading
import time

# Configuration
UPLOAD_FOLDER = '/media/soulstream'
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB max file size

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('soulstream.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_directory():
    """Ensure the upload directory exists"""
    if not os.path.exists(UPLOAD_FOLDER):
        try:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            logger.info(f"Created upload directory: {UPLOAD_FOLDER}")
        except Exception as e:
            logger.error(f"Failed to create upload directory: {e}")
            return False
    return True

def get_file_size(file_path):
    """Get file size in human readable format"""
    try:
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    except OSError:
        return "Unknown"

@app.route('/')
def index():
    """Serve the main upload page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SoulStream Media Server</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .file-list { margin-top: 20px; }
            .file-item { padding: 10px; border-bottom: 1px solid #eee; }
            .file-item:last-child { border-bottom: none; }
            .file-size { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 SoulStream Media Server</h1>
            <div class="info">
                <strong>Server Status:</strong> Running<br>
                <strong>Upload Directory:</strong> {{ upload_folder }}<br>
                <strong>Total Files:</strong> {{ file_count }}<br>
                <strong>Total Size:</strong> {{ total_size }}
            </div>
            <div class="file-list">
                <h3>Available Media Files:</h3>
                {% for file in files %}
                <div class="file-item">
                    <strong>{{ file.name }}</strong>
                    <span class="file-size">({{ file.size }})</span>
                </div>
                {% endfor %}
            </div>
            <p style="text-align: center; margin-top: 30px; color: #666;">
                Use the upload interface to add new media files to your collection.
            </p>
        </div>
    </body>
    </html>
    """
    
    # Get list of files in upload directory
    files = []
    total_size = 0
    file_count = 0
    
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    size = get_file_size(file_path)
                    files.append({'name': filename, 'size': size})
                    file_count += 1
                    # Calculate total size (simplified)
                    total_size = f"{file_count} files"
                except OSError:
                    continue
    
    return render_template_string(html_content, 
                                upload_folder=UPLOAD_FOLDER,
                                file_count=file_count,
                                total_size=total_size,
                                files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Ensure upload directory exists
        if not ensure_upload_directory():
            return jsonify({'error': 'Failed to create upload directory'}), 500
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Add timestamp to prevent overwrites
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}{ext}"
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the file
        file.save(file_path)
        
        # Log the upload
        file_size = get_file_size(file_path)
        logger.info(f"File uploaded: {filename} ({file_size})")
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'size': file_size
        }), 200
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/files')
def list_files():
    """List all uploaded files"""
    try:
        files = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                if allowed_file(filename):
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    try:
                        stat = os.stat(file_path)
                        files.append({
                            'name': filename,
                            'size': get_file_size(file_path),
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    except OSError:
                        continue
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': 'Failed to list files'}), 500

@app.route('/files/<filename>')
def serve_file(filename):
    """Serve a specific file"""
    try:
        if not allowed_file(filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_from_directory(UPLOAD_FOLDER, filename)
        
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({'error': 'Failed to serve file'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'upload_folder': UPLOAD_FOLDER,
        'upload_folder_exists': os.path.exists(UPLOAD_FOLDER)
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

def start_server(host='0.0.0.0', port=8080, debug=False):
    """Start the Flask server"""
    logger.info(f"Starting SoulStream Media Server on {host}:{port}")
    logger.info(f"Upload folder: {UPLOAD_FOLDER}")
    
    # Ensure upload directory exists
    ensure_upload_directory()
    
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='SoulStream Media Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--upload-folder', default=UPLOAD_FOLDER, help='Upload folder path')
    
    args = parser.parse_args()
    
    # Update upload folder if specified
    if args.upload_folder != UPLOAD_FOLDER:
        UPLOAD_FOLDER = args.upload_folder
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    start_server(args.host, args.port, args.debug) 
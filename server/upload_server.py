#!/usr/bin/env python3
"""
SoulStream Upload Server for Raspberry Pi
Handles file uploads from the Flutter app
"""

import os
import sys
import json
import shutil
from pathlib import Path
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/soulstream_upload.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = '/media/soulstream'
ALLOWED_EXTENSIONS = {
    'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v',
    '3gp', 'ts', 'mts', 'm2ts', 'vob', 'ogv', 'mxf', 'asf'
}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_path(filename, upload_id):
    """Generate file path for upload"""
    # Create directory for upload ID if it doesn't exist
    upload_dir = os.path.join(UPLOAD_FOLDER, upload_id)
    os.makedirs(upload_dir, exist_ok=True)
    return os.path.join(upload_dir, filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get upload parameters
        chunk_index = int(request.form.get('chunk_index', 0))
        total_chunks = int(request.form.get('total_chunks', 1))
        file_size = int(request.form.get('file_size', 0))
        upload_id = request.form.get('upload_id', 'default')
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Get file path
        file_path = get_file_path(filename, upload_id)
        
        # Handle chunked upload
        if total_chunks > 1:
            # Create temporary chunk file
            chunk_path = f"{file_path}.chunk_{chunk_index}"
            
            # Save chunk
            file.save(chunk_path)
            
            # If this is the last chunk, combine all chunks
            if chunk_index == total_chunks - 1:
                logging.info(f"Combining {total_chunks} chunks for {filename}")
                
                with open(file_path, 'wb') as outfile:
                    for i in range(total_chunks):
                        chunk_file = f"{file_path}.chunk_{i}"
                        if os.path.exists(chunk_file):
                            with open(chunk_file, 'rb') as infile:
                                shutil.copyfileobj(infile, outfile)
                            os.remove(chunk_file)  # Clean up chunk file
                
                logging.info(f"File {filename} uploaded successfully")
                return jsonify({
                    'message': 'File uploaded successfully',
                    'filename': filename,
                    'size': os.path.getsize(file_path)
                })
            else:
                return jsonify({
                    'message': f'Chunk {chunk_index + 1}/{total_chunks} uploaded',
                    'chunk_index': chunk_index
                })
        else:
            # Single file upload
            file.save(file_path)
            logging.info(f"File {filename} uploaded successfully")
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'size': os.path.getsize(file_path)
            })
    
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def server_status():
    """Get server status"""
    try:
        # Check disk space
        total, used, free = shutil.disk_usage(UPLOAD_FOLDER)
        
        # Count files in upload directory
        file_count = 0
        total_size = 0
        for root, dirs, files in os.walk(UPLOAD_FOLDER):
            file_count += len(files)
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
        
        return jsonify({
            'status': 'running',
            'upload_folder': UPLOAD_FOLDER,
            'disk_total': total,
            'disk_used': used,
            'disk_free': free,
            'file_count': file_count,
            'total_size': total_size
        })
    
    except Exception as e:
        logging.error(f"Status error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/files', methods=['GET'])
def list_files():
    """List uploaded files"""
    try:
        files = []
        for root, dirs, filenames in os.walk(UPLOAD_FOLDER):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'path': file_path,
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })
        
        return jsonify({'files': files})
    
    except Exception as e:
        logging.error(f"List files error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    logging.info(f"Starting SoulStream Upload Server")
    logging.info(f"Upload folder: {UPLOAD_FOLDER}")
    logging.info(f"Allowed extensions: {ALLOWED_EXTENSIONS}")
    
    # Run the server
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        threaded=True
    ) 
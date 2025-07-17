# SoulStream Uploader

A Flutter app for uploading movie files to a Raspberry Pi with advanced features like background uploads, pause/resume functionality, and unlimited simultaneous uploads.

## Features

- **Unlimited File Selection**: Select multiple movie files at once
- **Simultaneous Uploads**: Upload multiple files simultaneously
- **Pause/Resume**: Pause and resume uploads at any time
- **Background Uploads**: Uploads continue when app is in background
- **Progress Tracking**: Real-time progress for each file
- **Chunked Uploads**: Large files are uploaded in chunks for reliability
- **Error Handling**: Robust error handling with retry functionality
- **Modern UI**: Beautiful Material Design 3 interface

## Supported File Types

- MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V
- 3GP, TS, MTS, M2TS, VOB, OGV, MXF, ASF

## Setup Instructions

### 1. Raspberry Pi Server Setup

#### Prerequisites
- Raspberry Pi with Python 3.7+
- External storage mounted at `/media/soulstream`

#### Installation

1. **Install Python dependencies**:
   ```bash
   cd server
   pip3 install -r requirements.txt
   ```

2. **Create upload directory**:
   ```bash
   sudo mkdir -p /media/soulstream
   sudo chown pi:pi /media/soulstream
   ```

3. **Start the server**:
   ```bash
   python3 upload_server.py
   ```

4. **For production, use systemd service**:
   ```bash
   sudo cp soulstream-upload.service /etc/systemd/system/
   sudo systemctl enable soulstream-upload
   sudo systemctl start soulstream-upload
   ```

### 2. Flutter App Setup

#### Prerequisites
- Flutter SDK 3.0.0+
- Android Studio / VS Code
- Android device or emulator

#### Installation

1. **Install dependencies**:
   ```bash
   flutter pub get
   ```

2. **Update server IP** (if different from 192.168.18.20):
   - Edit `lib/services/upload_service.dart`
   - Change `_baseUrl` to your Raspberry Pi's IP address

3. **Build and run**:
   ```bash
   flutter run
   ```

4. **Build APK**:
   ```bash
   flutter build apk --release
   ```

## Configuration

### Server Configuration

Edit `server/upload_server.py` to modify:
- `UPLOAD_FOLDER`: Directory where files are saved
- `ALLOWED_EXTENSIONS`: Supported file types
- `MAX_CONTENT_LENGTH`: Maximum file size

### App Configuration

Edit `lib/services/upload_service.dart` to modify:
- `_baseUrl`: Server IP address
- `_chunkSize`: Upload chunk size (default: 1MB)

## Usage

### Uploading Files

1. Tap the "Upload Files" button
2. Select one or more movie files
3. Files will start uploading immediately
4. Monitor progress in the app

### Managing Uploads

- **Pause/Resume**: Swipe left on an upload and tap pause/resume
- **Cancel**: Swipe left and tap cancel
- **Retry**: For failed uploads, swipe left and tap retry
- **Remove**: Swipe left and tap remove to delete from history

### Background Uploads

The app supports background uploads:
- Uploads continue when app is minimized
- Progress is saved and restored on app restart
- Failed uploads can be retried

## Troubleshooting

### Common Issues

1. **Permission Denied**:
   - Grant storage permissions in app settings
   - Ensure server directory has proper permissions

2. **Network Connection**:
   - Verify Raspberry Pi IP address
   - Check network connectivity
   - Ensure server is running on port 8080

3. **Large File Uploads**:
   - Increase chunk size for better performance
   - Check available disk space on Pi

### Server Logs

Check server logs at `/var/log/soulstream_upload.log`:
```bash
tail -f /var/log/soulstream_upload.log
```

### App Logs

Enable debug mode in Flutter:
```bash
flutter run --debug
```

## API Endpoints

### POST /upload
Upload a file chunk
- `file`: File data
- `chunk_index`: Current chunk index
- `total_chunks`: Total number of chunks
- `file_size`: Total file size
- `upload_id`: Unique upload identifier

### GET /status
Get server status and disk usage

### GET /files
List all uploaded files

### GET /health
Health check endpoint

## Security Considerations

- The server accepts HTTP connections (not HTTPS)
- File validation is performed on server side
- Filenames are sanitized to prevent path traversal
- Consider adding authentication for production use

## Performance Tips

1. **Network**: Use wired connection for better upload speeds
2. **Storage**: Use SSD or fast storage on Raspberry Pi
3. **Chunk Size**: Adjust chunk size based on network conditions
4. **Concurrent Uploads**: Limit simultaneous uploads based on Pi performance

## License

This project is open source and available under the MIT License. 
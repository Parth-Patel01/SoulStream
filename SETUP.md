# Quick Setup Guide

## For Raspberry Pi (Server)

1. **Copy files to Pi**:
   ```bash
   scp -r server/ pi@192.168.18.20:~/soulstream-uploader/
   ```

2. **SSH into Pi**:
   ```bash
   ssh pi@192.168.18.20
   ```

3. **Run installation**:
   ```bash
   cd soulstream-uploader/server
   chmod +x install.sh
   ./install.sh
   ```

4. **Verify server is running**:
   ```bash
   curl http://192.168.18.20:8080/health
   ```

## For Flutter App

1. **Install Flutter dependencies**:
   ```bash
   flutter pub get
   ```

2. **Update server IP** (if needed):
   - Open `lib/services/upload_service.dart`
   - Change `_baseUrl` to your Pi's IP address

3. **Run the app**:
   ```bash
   flutter run
   ```

4. **Build APK**:
   ```bash
   flutter build apk --release
   ```

## Testing

1. **Start server on Pi**:
   ```bash
   python3 upload_server.py
   ```

2. **Run Flutter app**:
   ```bash
   flutter run
   ```

3. **Test upload**:
   - Tap "Upload Files"
   - Select a movie file
   - Watch progress in real-time

## Troubleshooting

### Server Issues
- Check if port 8080 is open: `sudo netstat -tlnp | grep 8080`
- Check logs: `tail -f /var/log/soulstream_upload.log`
- Restart service: `sudo systemctl restart soulstream-upload`

### App Issues
- Check network connectivity
- Verify Pi IP address in `upload_service.dart`
- Enable debug mode: `flutter run --debug`

### Permission Issues
- Grant storage permissions in Android settings
- Ensure `/media/soulstream` has proper permissions on Pi 
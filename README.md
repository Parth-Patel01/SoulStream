# 🎬 SoulStream Media Server

A modern, responsive web application for uploading and serving media files to your Raspberry Pi media server. Features unlimited simultaneous uploads with pause/resume functionality and seamless integration with Plex, Jellyfin, and other media servers.

## ✨ Features

- **Modern Web Interface**: Beautiful, responsive design that works on desktop and mobile
- **Drag & Drop Upload**: Easy file selection with visual feedback
- **Unlimited Simultaneous Uploads**: Upload multiple files at once
- **Pause/Resume**: Control upload progress with pause and resume functionality
- **Real-time Progress**: Live progress tracking with upload speed
- **File Type Support**: MP4, MKV, AVI, MOV, WMV, FLV, WEBM
- **Large File Support**: Handles files up to 16GB
- **Media Server Integration**: Perfect for Plex, Jellyfin, and other media servers
- **Automatic Service**: Runs as a system service with auto-restart

## 🚀 Quick Start

### Prerequisites

- Raspberry Pi (3 or 4 recommended)
- Raspberry Pi OS (or any Linux distribution)
- Internet connection for installation
- External storage (recommended for large media collections)

### Installation

1. **Clone or download this repository to your Raspberry Pi:**
   ```bash
   git clone <repository-url>
   cd SoulStream-2
   ```

2. **Run the installation script:**
   ```bash
   sudo chmod +x install.sh
   sudo ./install.sh
   ```

3. **Access your media server:**
   - Direct server: `http://your-pi-ip:8080`
   - Nginx proxy: `http://your-pi-ip`

## 📁 File Structure

```
SoulStream-2/
├── index.html          # Main web interface
├── styles.css          # Modern CSS styling
├── script.js           # JavaScript functionality
├── server.py           # Flask backend server
├── requirements.txt    # Python dependencies
├── install.sh          # Installation script
└── README.md          # This file
```

## 🎯 Usage

### Web Interface

1. **Open your browser** and navigate to `http://your-pi-ip:8080`
2. **Drag and drop** movie files onto the upload area or click to browse
3. **Click "Start Upload"** to begin uploading files
4. **Monitor progress** with real-time progress bars and upload speeds
5. **Pause/Resume** uploads as needed

### File Management

- **Upload Directory**: `/media/soulstream/`
- **File Naming**: Files are automatically renamed with timestamps to prevent conflicts
- **Supported Formats**: MP4, MKV, AVI, MOV, WMV, FLV, WEBM

## 🔧 Management Commands

### Service Management
```bash
# Check service status
soulstream-status

# View logs
journalctl -u soulstream -f

# Restart service
sudo systemctl restart soulstream

# Stop service
sudo systemctl stop soulstream

# Start service
sudo systemctl start soulstream
```

### File Management
```bash
# Create backup
soulstream-backup

# Clean up all files
soulstream-cleanup

# View uploaded files
ls -la /media/soulstream/
```

## 🎬 Media Server Integration

### Plex Integration

1. **Install Plex Media Server** on your Raspberry Pi
2. **Add Media Library** in Plex:
   - Library Type: Movies
   - Folder: `/media/soulstream/`
3. **Scan Library** to detect uploaded files

### Jellyfin Integration

1. **Install Jellyfin** on your Raspberry Pi
2. **Add Media Library** in Jellyfin:
   - Content Type: Movies
   - Path: `/media/soulstream/`
3. **Scan Library** to detect uploaded files

### Other Media Servers

The uploaded files are stored in `/media/soulstream/` and can be integrated with:
- **Emby**: Add as a media library
- **Kodi**: Add as a network source
- **VLC**: Open the directory as a playlist
- **Any DLNA server**: Point to the media directory

## 🔧 Configuration

### Server Configuration

Edit `/opt/soulstream/server.py` to modify:
- Upload directory path
- Maximum file size
- Allowed file types
- Server port

### Nginx Configuration

The installation script creates an Nginx reverse proxy. Edit `/etc/nginx/sites-available/soulstream` to customize:
- SSL certificates
- Custom domain
- Additional security headers

### Service Configuration

Edit `/etc/systemd/system/soulstream.service` to modify:
- Service user
- Working directory
- Environment variables
- Restart behavior

## 📊 Monitoring

### Logs
- **Application logs**: `/var/log/soulstream/`
- **System logs**: `journalctl -u soulstream`
- **Nginx logs**: `/var/log/nginx/`

### Health Check
```bash
# Check server health
curl http://your-pi-ip:8080/health

# List uploaded files
curl http://your-pi-ip:8080/files
```

## 🔒 Security Considerations

- **Firewall**: Port 8080 is opened automatically
- **User isolation**: Service runs as dedicated user
- **File permissions**: Proper ownership and permissions set
- **CORS**: Configured for web interface access
- **File validation**: Only video files are accepted

## 🛠️ Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   journalctl -u soulstream -f
   # Check for Python dependency issues
   ```

2. **Upload fails**
   - Check disk space: `df -h`
   - Check permissions: `ls -la /media/soulstream/`
   - Check logs: `journalctl -u soulstream`

3. **Web interface not accessible**
   - Check firewall: `sudo ufw status`
   - Check service: `systemctl status soulstream`
   - Check port: `netstat -tlnp | grep 8080`

4. **Large file uploads fail**
   - Increase timeout in Nginx config
   - Check available disk space
   - Verify network stability

### Performance Optimization

1. **Use external storage** for large media collections
2. **SSD storage** for better performance
3. **Gigabit network** for faster uploads
4. **Adequate cooling** for Raspberry Pi

## 📈 Advanced Features

### Custom Upload Directory
```bash
# Edit server.py and change UPLOAD_FOLDER
UPLOAD_FOLDER = '/path/to/your/media'

# Restart service
sudo systemctl restart soulstream
```

### Custom Port
```bash
# Edit install.sh and change PORT variable
PORT=9000

# Re-run installation or manually update service file
```

### SSL/HTTPS Setup
1. Obtain SSL certificate
2. Update Nginx configuration
3. Redirect HTTP to HTTPS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Flask web framework
- Font Awesome icons
- Modern CSS techniques
- Raspberry Pi community

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs and error messages
3. Create an issue in the repository
4. Check the documentation

---

**Happy streaming! 🎬✨** 
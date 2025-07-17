@echo off
REM SoulStream Upload Server Installation Script
REM Run this script on your Raspberry Pi

echo Installing SoulStream Upload Server...

REM Update system
echo Updating system packages...
sudo apt update && sudo apt upgrade -y

REM Install Python dependencies
echo Installing Python dependencies...
sudo apt install -y python3 python3-pip python3-venv

REM Create virtual environment
echo Creating virtual environment...
python3 -m venv venv
call venv\Scripts\activate

REM Install Python packages
echo Installing Python packages...
pip install -r requirements.txt

REM Create upload directory
echo Creating upload directory...
sudo mkdir -p /media/soulstream
sudo chown pi:pi /media/soulstream
sudo chmod 755 /media/soulstream

REM Create log directory
echo Creating log directory...
sudo mkdir -p /var/log
sudo touch /var/log/soulstream_upload.log
sudo chown pi:pi /var/log/soulstream_upload.log

REM Install systemd service
echo Installing systemd service...
sudo cp soulstream-upload.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable soulstream-upload

REM Start the service
echo Starting SoulStream Upload Server...
sudo systemctl start soulstream-upload

REM Check service status
echo Checking service status...
sudo systemctl status soulstream-upload

echo.
echo Installation complete!
echo Server is running on http://%COMPUTERNAME%:8080
echo.
echo Useful commands:
echo   sudo systemctl status soulstream-upload  # Check service status
echo   sudo systemctl restart soulstream-upload # Restart service
echo   sudo systemctl stop soulstream-upload    # Stop service
echo   tail -f /var/log/soulstream_upload.log  # View logs
echo.
echo Upload directory: /media/soulstream 
# 📱 WebWatch - Smartphone CCTV Camera System

Transform your old smartphone into a powerful CCTV camera system with real-time streaming, recording, and remote monitoring capabilities.

## 🌟 Features

- **Dynamic IP Detection**: Automatically adapts to your network configuration
- **Real-time Video Streaming**: WebRTC-based peer-to-peer connection
- **Secure HTTPS**: Self-signed SSL certificates for encrypted communication
- **Recording & Playback**: Save and review recorded footage
- **Multi-device Support**: Access from any device on your network
- **User Authentication**: Secure login system
- **Room-based Connections**: Connect multiple cameras with unique codes

## 🚀 Quick Start

### 1. Automatic Installation
```cmd
install.bat
```

### 2. Start the System
```cmd
# Terminal 1 - Backend Server
start_backend.bat

# Terminal 2 - Frontend Interface
start_frontend.bat
```

### 3. Access the System
- **Web Interface**: `https://YOUR_IP:3000`
- **API Backend**: `https://YOUR_IP:5000`
- **Default Login**: `admin` / `123`

## 🔧 Manual Setup

### Prerequisites
- Python 3.7+
- Node.js 14+
- npm

### Backend Setup
```cmd
cd backend
pip install -r requirements.txt
python setup_db.py
python generate_cert.py
```

### Frontend Setup
```cmd
cd WebWatch
npm install
```

## 🌐 Network Configuration

### Dynamic IP Detection
The system automatically detects your current IP address:
```cmd
cd backend
python get_ip.py
```

### Manual IP Configuration
Set a custom backend URL:
```cmd
set REACT_APP_BACKEND_URL=https://your-ip:5000
```

## 📱 How to Use

1. **Setup**: Run the installation and start both servers
2. **Login**: Access the web interface and login with admin/123
3. **Generate Code**: Click "Generate Camera Code" to get a 6-digit code
4. **Connect Camera**: Use the code to connect your smartphone camera
5. **Monitor**: View live feed and control recording from the dashboard

## 🔒 Security Features

- **HTTPS Encryption**: All communication is encrypted
- **Self-signed Certificates**: Automatic SSL certificate generation
- **User Authentication**: Secure login system
- **CORS Protection**: Configured for secure cross-origin requests

## 🛠️ Troubleshooting

### Common Issues

**Port Already in Use**
```cmd
# Kill processes on ports 3000 and 5000
netstat -ano | findstr :3000
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

**SSL Certificate Errors**
```cmd
cd backend
python generate_cert.py
```

**Network Connection Issues**
- Check Windows Firewall settings
- Ensure devices are on the same network
- Verify IP address with `python get_ip.py`

**Dependencies Not Installing**
```cmd
# Update pip and npm
python -m pip install --upgrade pip
npm install -g npm@latest
```

## 🧪 Testing

Run the comprehensive test suite:
```cmd
python test_setup.py
```

## 📁 Project Structure

```
Old-smartphone-as-CCTV-camera/
├── backend/                 # Python Flask backend
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration with dynamic IP
│   ├── setup_db.py         # Database initialization
│   ├── generate_cert.py    # SSL certificate generation
│   ├── get_ip.py           # IP detection utility
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   └── sockets/            # WebSocket handlers
├── WebWatch/               # React frontend
│   ├── src/
│   │   ├── config.js       # Dynamic backend URL configuration
│   │   └── ...             # React components
│   └── public/
├── install.bat             # Automatic installation script
├── start_backend.bat       # Backend startup script
├── start_frontend.bat      # Frontend startup script
├── test_setup.py          # Comprehensive test suite
└── README.md              # This file
```

## 🔧 Configuration Files

### Backend Configuration (`backend/config.py`)
- Dynamic IP detection
- Environment variable support
- CORS configuration

### Frontend Configuration (`WebWatch/src/config.js`)
- Automatic host detection
- Development/production modes
- Environment variable override

### Environment Variables (`WebWatch/.env`)
- HTTPS configuration
- SSL certificate paths
- Custom backend URL support

## 🌍 Network Access

### Local Network
- Devices on the same WiFi can access using your computer's IP
- Use the IP address shown when starting the backend

### External Access
1. Configure router port forwarding (ports 3000, 5000)
2. Use your public IP address
3. Consider using a dynamic DNS service

## 📊 System Requirements

- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 1GB for application, additional space for recordings
- **Network**: WiFi or Ethernet connection
- **Browser**: Modern browser with WebRTC support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter issues:
1. Run `python test_setup.py` to diagnose problems
2. Check the troubleshooting section
3. Verify network connectivity and firewall settings
4. Ensure all dependencies are properly installed

---

**Happy Monitoring! 📹🔒**
# WebWatch - Turn Your Old Phone into a Security Camera

Got an old smartphone lying around? This project lets you use it as a CCTV camera with live streaming and recording.

## What it does

- Stream live video from your phone to any browser
- Record and playback footage
- Connect multiple cameras using room codes
- Works on your local network with HTTPS

## Getting Started

You'll need Python 3.7+ and Node.js installed.

**Easy way:**
```cmd
install.bat
```

Then start both servers:
```cmd
start_backend.bat
start_frontend.bat
```

Open `https://YOUR_IP:3000` in your browser. Login with `admin` / `123`.

## Manual Setup

If the batch files don't work:

```cmd
cd backend
pip install -r requirements.txt
python setup_db.py
python generate_cert.py
python app.py
```

In another terminal:
```cmd
cd WebWatch
npm install
npm start
```

## How to Use

1. Open the web interface and login
2. Click "Generate Camera Code" to get a 6-digit code
3. Enter that code on your phone's camera
4. Start watching the live feed

The system finds your IP automatically. If you need to check it manually, run `python get_ip.py` in the backend folder.

## Common Problems

**Port already in use?**
```cmd
netstat -ano | findstr :3000
taskkill /PID <number> /F
```

**SSL errors?**
```cmd
cd backend
python generate_cert.py
```

**Can't connect?**
Make sure both devices are on the same WiFi and check your firewall settings.

## Project Structure

```
backend/        - Flask server, handles video streaming
WebWatch/       - React frontend, the web interface
*.bat           - Quick start scripts for Windows
```

That's it. Simple security camera system using stuff you already have.
# Frontend-Backend Connection Guide

## 📋 Overview

Yeh document explain karta hai ki kaise **Frontend (React)** aur **Backend (Flask)** ek saath connect hote hain aur kaise data flow hota hai.

---

## 🔌 Connection Architecture

```
Frontend (React - Port 3000)
    ↓
    ↓ HTTP Requests (fetch API)
    ↓ WebSocket (Socket.IO)
    ↓
Backend (Flask - Port 5000)
```

---

## 📁 File Structure

### Frontend Files (WebWatch/src/)
```
src/
├── config.js          → Backend URLs aur endpoints define karta hai
├── api.js             → API call functions (helper functions)
├── App.js             → Main app component
├── Login.js           → Login page (Backend connected)
├── Dashboard.js       → Camera dashboard (Backend + Socket.IO connected)
├── Broadcast.js       → Camera streaming page (Backend + Socket.IO connected)
└── ...
```

### Backend Files (backend/)
```
backend/
├── app.py             → Main Flask application
├── config.py          → Configuration settings
├── routes/
│   ├── auth.py        → Login API endpoint
│   ├── code.py        → Code generation endpoint
│   ├── camera.py      → Camera registration endpoint
│   └── ...
└── sockets/
    ├── basic.py       → Basic Socket.IO events
    ├── rooms.py       → Room management (code-based pairing)
    └── signaling.py   → WebRTC signaling
```

---

## 🔗 How Components Connect

### 1. Login.js → Backend API

**Flow:**
1. User email aur password enter karta hai
2. Frontend `api.js` ka `login()` function call karta hai
3. HTTP POST request backend ko bhejta hai: `POST /api/auth/login`
4. Backend credentials check karta hai (username="admin", password="123")
5. Response return hota hai: `{status: "ok"}` ya error
6. Agar success, user ko Dashboard par redirect kiya jata hai

**Code Connection:**
```javascript
// Login.js
import { login } from './api';

const result = await login(email, password);
if (result.success) {
  navigate('/dashboard');
}
```

**Backend Endpoint:**
```
POST http://localhost:5000/api/auth/login
Body: { "username": "admin", "password": "123" }
Response: { "status": "ok", "message": "login successful" }
```

---

### 2. Dashboard.js → Backend API + Socket.IO

**Flow:**
1. User "Add New Camera" button click karta hai
2. Frontend `api.js` ka `generateCode()` function call karta hai
3. Backend random 6-digit code generate karta hai
4. Code user ko dikhaya jata hai (modal mein)
5. Socket.IO se room join hota hai (viewer ke taur par)
6. Camera jab same code se connect karega, tab room mein match hoga

**Code Connection:**
```javascript
// Dashboard.js
import { generateCode } from './api';
import io from 'socket.io-client';

const result = await generateCode(); // Backend se code generate
socket.emit('join_room', { code: result.code, type: 'viewer' });
```

**Backend Endpoints:**
```
GET http://localhost:5000/api/code/generate
Response: { "code": "123456" }

Socket.IO Event: 'join_room'
Data: { "code": "123456", "type": "viewer" }
```

---

### 3. Broadcast.js → Backend API + Socket.IO + Camera

**Flow:**
1. User 6-digit code enter karta hai (Dashboard se mila hua)
2. Camera permission request hota hai (getUserMedia)
3. Socket.IO se room join hota hai (camera ke taur par)
4. Backend ko camera register karta hai
5. Video stream start hota hai
6. Jab viewer same room mein hoga, tab signaling start hoga (future WebRTC)

**Code Connection:**
```javascript
// Broadcast.js
import { registerCamera } from './api';
import io from 'socket.io-client';

const stream = await navigator.mediaDevices.getUserMedia({ video: true });
socket.emit('join_room', { code: enteredCode, type: 'camera' });
await registerCamera(`Camera-${enteredCode}`);
```

**Backend Endpoints:**
```
POST http://localhost:5000/api/camera/register
Body: { "name": "Camera-123456" }
Response: { "status": "ok", "camera": "Camera-123456" }

Socket.IO Event: 'join_room'
Data: { "code": "123456", "type": "camera" }
```

---

## 🔄 Data Flow Examples

### Example 1: Login Process
```
User → Login.js
  ↓
handleLogin() function
  ↓
api.js → login(email, password)
  ↓
HTTP POST → http://localhost:5000/api/auth/login
  ↓
Backend routes/auth.py → login() function
  ↓
Check credentials
  ↓
Response: {status: "ok"} or {status: "error"}
  ↓
Login.js → navigate('/dashboard')
```

### Example 2: Code Generation & Pairing
```
Dashboard.js → "Add Camera" click
  ↓
api.js → generateCode()
  ↓
HTTP GET → http://localhost:5000/api/code/generate
  ↓
Backend routes/code.py → generate_code()
  ↓
Random 6-digit code: "654321"
  ↓
Dashboard.js → Show code to user
  ↓
Socket.IO → socket.emit('join_room', {code: "654321", type: "viewer"})
  ↓
Backend sockets/rooms.py → handle_join_room()
  ↓
Room created/joined

---

Camera Device (Broadcast.js) → Enter code "654321"
  ↓
Socket.IO → socket.emit('join_room', {code: "654321", type: "camera"})
  ↓
Backend → Same room mein camera add
  ↓
Both devices same room mein! (Ready for WebRTC signaling)
```

---

## 🌐 Socket.IO Events

### Client → Server Events (Frontend se Backend)

| Event Name | Data | Description |
|------------|------|-------------|
| `join_room` | `{code: "123456", type: "camera"/"viewer"}` | Room join karna |
| `leave_room` | `{code: "123456"}` | Room se leave karna |
| `offer` | `{offer: {...}, room_code: "123456"}` | WebRTC offer bhejna |
| `answer` | `{answer: {...}, room_code: "123456"}` | WebRTC answer bhejna |
| `ice-candidate` | `{candidate: {...}, room_code: "123456"}` | ICE candidate bhejna |

### Server → Client Events (Backend se Frontend)

| Event Name | Data | Description |
|------------|------|-------------|
| `connected` | `{message: "...", status: "ok"}` | Connection confirmation |
| `join_room_success` | `{room_code: "123456", ...}` | Room join success |
| `join_room_error` | `{message: "...", status: "error"}` | Room join error |
| `room_update` | `{room_code: "123456", total_clients: 2}` | Room status update |
| `offer` | `{offer: {...}, from_socket_id: "..."}` | WebRTC offer receive |
| `answer` | `{answer: {...}, from_socket_id: "..."}` | WebRTC answer receive |
| `ice-candidate` | `{candidate: {...}, from_socket_id: "..."}` | ICE candidate receive |

---

## 🚀 How to Run

### Backend Start Karna:
```powershell
cd Old-smartphone-as-CCTV-camera\backend
.\venv\Scripts\Activate.ps1
python app.py
```
Backend `http://localhost:5000` par chalega.

### Frontend Start Karna:
```powershell
cd Old-smartphone-as-CCTV-camera\WebWatch
npm install  # Pehli baar dependencies install karega
npm start
```
Frontend `http://localhost:3000` par chalega.

---

## 📝 Important Notes

1. **CORS Configuration**: Backend mein CORS enable hai (`*`), toh frontend se easily API calls ho sakti hain.

2. **Socket.IO Connection**: Frontend aur backend dono Socket.IO use karte hain real-time communication ke liye. Default port: `5000`.

3. **Authentication**: Currently hardcoded credentials use ho rahe hain (username="admin", password="123"). Production mein database aur JWT tokens use karna chahiye.

4. **Camera Permissions**: Broadcast.js mein camera access ke liye browser permission chahiye. User ko allow karna hoga.

5. **Code Format**: Pairing codes 6 digits ke hain (100000-999999). Backend automatically generate karta hai.

---

## 🔧 Configuration Files

### Frontend: `src/config.js`
```javascript
const API_BASE_URL = 'http://localhost:5000';
const SOCKET_URL = 'http://localhost:5000';
```

### Backend: `backend/config.py`
```python
CORS_ORIGINS = "*"  # Development ke liye
BACKEND_BASE_URL = "http://localhost:5000"
```

Agar backend different port par chal raha hai, toh `config.js` mein URL update karna hoga.

---

## ✅ Testing Checklist

- [x] Login API connected
- [x] Code generation API connected
- [x] Camera registration API connected
- [x] Socket.IO connection established
- [x] Room joining working
- [x] Camera permissions working
- [ ] WebRTC signaling (TODO: Future implementation)

---

## 🎯 Next Steps (Future Improvements)

1. **WebRTC Implementation**: Actual video streaming ke liye WebRTC signaling complete karna
2. **Database Integration**: User accounts, camera list, recordings store karna
3. **Authentication**: JWT tokens use karna proper session management ke liye
4. **Error Handling**: Better error messages aur retry logic
5. **UI Improvements**: Loading states, better status indicators

---

**All Done! 🎉** Frontend aur Backend ab properly connected hain!


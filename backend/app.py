import sys
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from get_ip import get_local_ip

# Setup Paths
user_site = os.path.expanduser('~\\AppData\\Roaming\\Python\\Python314\\site-packages')
if user_site not in sys.path: sys.path.insert(0, user_site)

from routes.auth import auth_bp
from routes.camera import camera_bp
from routes.login import login_bp
from routes.code import code_bp
import config

# Socket.IO imports
from sockets.basic import init_socketio, register_basic_events
from sockets.rooms import register_room_events
from sockets.signaling import register_signaling_events
from sockets.fallback import register_fallback_events

# Get dynamic IP
LOCAL_IP = get_local_ip()
print(f"🌐 Server will run on IP: {LOCAL_IP}")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(config.Config)
CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(camera_bp, url_prefix="/api/camera")
app.register_blueprint(code_bp, url_prefix="/api/code")
app.register_blueprint(login_bp)

@app.route("/")
def home(): 
    return f"✅ BACKEND RUNNING ON {LOCAL_IP}:5001"

@app.route("/api/config")
def get_config():
    """API endpoint to get current server IP"""
    return {
        "backend_url": f"https://{LOCAL_IP}:5001",
        "socket_url": f"https://{LOCAL_IP}:5001",
        "ip": LOCAL_IP
    }

# API Tester page - for testing APIs in browser
@app.route("/test")
def test_page():
    return render_template("test_api.html")

# Socket.IO Tester page
@app.route("/socket-test")
def socket_test_page():
    return render_template("socket_test.html")

# Initialize Socket.IO
socketio = init_socketio(app)

# Register all Socket.IO events
register_basic_events(socketio)
register_room_events(socketio)
register_signaling_events(socketio)
register_fallback_events(socketio)

print("✅ Socket.IO initialized and all events registered!")
print("🔌 WebSocket server ready!")

@socketio.on('connect')
def handle_connect():
    print(f"🟢 Connected: {request.sid}")
    emit('connected', {'status': 'ok'})

@socketio.on('join_room')
def on_join_room(data):
    # ⚡ FORCE STRING: Converts 123456 -> "123456"
    raw = data.get('code') or data.get('room_code')
    if raw:
        room = str(raw).strip()
        join_room(room)
        print(f"🚪 Joined Room: '{room}'")
        emit('room_update', {'room_code': room, 'status': 'Live'}, to=room)

@socketio.on("offer")
def on_offer(data):
    # ⚡ FORCE STRING
    raw = data.get("room_code") or data.get("room") or data.get("code")
    if raw:
        room = str(raw).strip()
        print(f"📹 Forwarding OFFER to: '{room}'")
        emit("offer", data, room=room, include_self=False)

@socketio.on("answer")
def on_answer(data):
    raw = data.get("room_code") or data.get("room") or data.get("code")
    if raw:
        room = str(raw).strip()
        print(f"✅ Forwarding ANSWER to: '{room}'")
        emit("answer", data, room=room, include_self=False)

@socketio.on("ice-candidate")
def on_ice_candidate(data):
    raw = data.get("room_code") or data.get("room") or data.get("code")
    if raw:
        room = str(raw).strip()
        emit("ice-candidate", data, room=room, include_self=False)

if __name__ == "__main__":
    import os
    if os.path.exists("cert.pem"):
        print(f"🔒 Starting HTTPS server on {LOCAL_IP}:5001")
        socketio.run(app, host="0.0.0.0", port=5001, debug=True, allow_unsafe_werkzeug=True, ssl_context=("cert.pem", "key.pem"))
    else:
        print(f"🌐 Starting HTTP server on {LOCAL_IP}:5001")
        socketio.run(app, host="0.0.0.0", port=5001, debug=True, allow_unsafe_werkzeug=True)
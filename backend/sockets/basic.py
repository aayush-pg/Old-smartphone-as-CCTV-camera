from flask_socketio import SocketIO, emit
from flask import request

socketio = None

def init_socketio(app):
    global socketio
    # ⚠️ THIS FIXES THE 400 ERROR (Increases limit to 10MB)
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*", 
        max_http_buffer_size=1e7,  # 👈 CRITICAL FIX
        ping_timeout=60,
        ping_interval=25
    )
    return socketio

def register_basic_events(socketio_instance):
    @socketio_instance.on('connect')
    def handle_connect():
        print(f"[SUCCESS] Client connected! Socket ID: {request.sid}")
        emit('connected', {'status': 'ok'})
    
    @socketio_instance.on('disconnect')
    def handle_disconnect():
        print(f"[INFO] Client disconnected! Socket ID: {request.sid}")

    @socketio_instance.on('ping')
    def handle_ping(data):
        emit('pong', {'status': 'ok'})
    
    @socketio_instance.on('message')
    def handle_message(data):
        emit('message_response', {'echo': data})
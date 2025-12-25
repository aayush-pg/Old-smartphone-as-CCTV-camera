"""
Backend Member 1 - WebSocket & SocketIO Fundamentals
यह file basic Socket.IO setup handle करती है

Concepts:
- HTTP vs WebSocket: HTTP एक request-response protocol है, 
  WebSocket एक persistent connection है जो real-time communication enable करता है
- Real-time communication: Data instantly send/receive होता है, 
  page refresh की जरूरत नहीं
- Socket.IO events: connect, disconnect, emit, on
"""

from flask_socketio import SocketIO, emit
from flask import request

# SocketIO instance को बाहर से initialize किया जाएगा
socketio = None

def init_socketio(app):
    """
    SocketIO को initialize करता है
    app: Flask application instance
    """
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*")
    return socketio

def register_basic_events(socketio_instance):
    """
    Basic Socket.IO events register करता है:
    - connect: जब client server से connect होता है
    - disconnect: जब client disconnect होता है
    - ping: Test event (ping-pong mechanism)
    """
    
    @socketio_instance.on('connect')
    def handle_connect():
        """
        जब कोई client connect होता है, यह function automatically call होता है
        """
        socket_id = request.sid
        print(f"[SUCCESS] Client connected! Socket ID: {socket_id}")
        # Client को confirmation भेजते हैं
        emit('connected', {'message': 'Server se connect ho gaya!', 'status': 'ok'})
    
    @socketio_instance.on('disconnect')
    def handle_disconnect():
        """
        जब कोई client disconnect होता है, यह function automatically call होता है
        """
        socket_id = request.sid
        print(f"[INFO] Client disconnected! Socket ID: {socket_id}")
        # Note: Cannot emit after disconnect as connection is already closed
    
    @socketio_instance.on('ping')
    def handle_ping(data):
        """
        Ping-Pong Test Event
        Client 'ping' event भेजेगा, server 'pong' response भेजेगा
        
        data: Client से आने वाला data (optional)
        """
        print(f"[INFO] Ping received from client: {data}")
        # Pong response भेजते हैं
        emit('pong', {
            'message': 'Pong! Server ne ping receive kiya',
            'original_data': data,
            'status': 'ok'
        })
    
    @socketio_instance.on('message')
    def handle_message(data):
        """
        Generic message handler
        Client किसी भी message को 'message' event के साथ भेज सकता है
        """
        print(f"[INFO] Message received: {data}")
        # Echo back करते हैं (same message वापस भेजते हैं)
        emit('message_response', {
            'echo': data,
            'status': 'ok'
        })

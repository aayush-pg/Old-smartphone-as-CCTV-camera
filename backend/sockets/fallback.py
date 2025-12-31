"""
Video Fallback System - 1 Second Delay Streaming
यह system WebRTC fail होने पर frames को 1 second delay के साथ stream करता है
"""

from flask_socketio import emit, join_room, leave_room
from flask import request
import base64
import time

# Fallback rooms storage
fallback_rooms = {}

def register_fallback_events(socketio_instance):
    """
    Fallback streaming events register करता है
    """
    
    @socketio_instance.on('join_fallback_room')
    def handle_join_fallback_room(data):
        """
        Fallback room में join करने के लिए
        """
        try:
            room_code = data.get('room_code', '').strip()
            device_type = data.get('type', 'viewer')
            socket_id = request.sid
            
            if not room_code:
                emit('fallback_error', {'message': 'Room code required'})
                return
            
            # Join room
            join_room(f"fallback_{room_code}")
            
            # Track in fallback rooms
            if room_code not in fallback_rooms:
                fallback_rooms[room_code] = []
            
            if socket_id not in fallback_rooms[room_code]:
                fallback_rooms[room_code].append(socket_id)
            
            print(f"[FALLBACK] {device_type} joined fallback room {room_code}")
            
            emit('fallback_joined', {
                'room_code': room_code,
                'device_type': device_type,
                'status': 'ok'
            })
            
        except Exception as e:
            print(f"[ERROR] Fallback join error: {e}")
            emit('fallback_error', {'message': str(e)})
    
    @socketio_instance.on('fallback_frame')
    def handle_fallback_frame(data):
        """
        Fallback frame को dashboard पर forward करता है
        """
        try:
            room_code = data.get('room_code')
            frame_data = data.get('frame_data')
            timestamp = data.get('timestamp')
            width = data.get('width', 640)
            height = data.get('height', 480)
            
            if not room_code or not frame_data:
                return
            
            # Forward frame to dashboard viewers in the same room
            socketio_instance.emit('fallback_frame', {
                'room_code': room_code,
                'frame_data': frame_data,
                'timestamp': timestamp,
                'width': width,
                'height': height
            }, room=f"fallback_{room_code}", skip_sid=request.sid)
            
            # Optional: Log frame info (comment out for performance)
            # print(f"[FALLBACK] Frame forwarded for room {room_code} ({width}x{height})")
            
        except Exception as e:
            print(f"[ERROR] Fallback frame error: {e}")
    
    @socketio_instance.on('leave_fallback_room')
    def handle_leave_fallback_room(data):
        """
        Fallback room से leave करने के लिए
        """
        try:
            room_code = data.get('room_code', '').strip()
            socket_id = request.sid
            
            if room_code:
                leave_room(f"fallback_{room_code}")
                
                # Remove from fallback rooms
                if room_code in fallback_rooms and socket_id in fallback_rooms[room_code]:
                    fallback_rooms[room_code].remove(socket_id)
                    
                    if len(fallback_rooms[room_code]) == 0:
                        del fallback_rooms[room_code]
                
                print(f"[FALLBACK] Client left fallback room {room_code}")
                
        except Exception as e:
            print(f"[ERROR] Fallback leave error: {e}")
    
    @socketio_instance.on('disconnect')
    def handle_fallback_disconnect_cleanup():
        """
        Disconnect पर fallback rooms से cleanup
        """
        socket_id = request.sid
        
        # Clean up from all fallback rooms
        rooms_to_cleanup = []
        for room_code, clients in fallback_rooms.items():
            if socket_id in clients:
                clients.remove(socket_id)
                rooms_to_cleanup.append(room_code)
                
                if len(clients) == 0:
                    del fallback_rooms[room_code]
        
        if rooms_to_cleanup:
            print(f"[FALLBACK] Cleaned up socket {socket_id} from {len(rooms_to_cleanup)} fallback room(s)")
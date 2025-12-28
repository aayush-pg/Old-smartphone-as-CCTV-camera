"""
Backend Member 3 - Rooms & Matching Logic
यह file code-based room matching handle करती है

Concepts:
- Socket.IO rooms: Clients को groups में organize करने का तरीका
- join_room(): Client को specific room में add करता है
- leave_room(): Client को room से remove करता है
- In-memory storage: Dictionary में rooms और connected clients store करते हैं
"""

from flask_socketio import emit, join_room, leave_room
from flask import request

# In-memory storage: Rooms dictionary
# Format: {"123456": ["socket_id_1", "socket_id_2"]}
# Key = 6-digit room code
# Value = List of socket IDs in that room
rooms = {}

def register_room_events(socketio_instance):
    """
    Room-related Socket.IO events register करता है
    """
    
    @socketio_instance.on('join_room')
    def handle_join_room(data):
        """
        Client room में join करने के लिए यह event use करता है
        
        Expected data format:
        {
            "code": "123456",  # 6-digit room code
            "type": "camera" or "viewer"  # Device type
        }
        """
        try:
            # Data extract करते हैं
            room_code = data.get('code', '').strip()
            device_type = data.get('type', 'viewer')  # Default: viewer
            socket_id = request.sid  # Current client का socket ID
            
            # Validation: Code 6 digits होना चाहिए
            if not room_code or len(room_code) != 6 or not room_code.isdigit():
                emit('join_room_error', {
                    'message': 'Invalid room code! 6-digit code required.',
                    'status': 'error'
                })
                return
            
            # Special validation for camera devices
            if device_type == 'camera':
                # Check if room exists (dashboard must create room first)
                if room_code not in rooms or len(rooms[room_code]) == 0:
                    emit('join_room_error', {
                        'message': 'Room not found! Please check the code.',
                        'status': 'error'
                    })
                    return
                
                print(f"[INFO] Camera trying to join existing room {room_code} with {len(rooms[room_code])} clients")
            
            # Room में join करते हैं
            join_room(room_code)
            
            # Rooms dictionary में add करते हैं
            if room_code not in rooms:
                rooms[room_code] = []
            
            # Socket ID add करते हैं (अगर पहले से नहीं है)
            if socket_id not in rooms[room_code]:
                rooms[room_code].append(socket_id)
            
            print(f"[SUCCESS] {device_type} joined room {room_code}. Socket ID: {socket_id}")
            print(f"[INFO] Room {room_code} now has {len(rooms[room_code])} client(s)")
            
            # Success confirmation भेजते हैं
            emit('join_room_success', {
                'message': f'Room {room_code} me successfully join ho gaya!',
                'room_code': room_code,
                'device_type': device_type,
                'clients_in_room': len(rooms[room_code]),
                'status': 'ok'
            })
            
            # Same room के सभी clients को notify करते हैं
            socketio_instance.emit('room_update', {
                'message': f'{device_type} ne room join kiya',
                'room_code': room_code,
                'total_clients': len(rooms[room_code]),
                'status': 'ok'
            }, room=room_code)
            
        except Exception as e:
            print(f"[ERROR] Error in join_room: {e}")
            emit('join_room_error', {
                'message': f'Error: {str(e)}',
                'status': 'error'
            })
    
    @socketio_instance.on('leave_room')
    def handle_leave_room(data):
        """
        Client room से leave करने के लिए यह event use करता है
        
        Expected data format:
        {
            "code": "123456"  # 6-digit room code
        }
        """
        try:
            room_code = data.get('code', '').strip()
            socket_id = request.sid
            
            if not room_code:
                emit('leave_room_error', {
                    'message': 'Room code required!',
                    'status': 'error'
                })
                return
            
            # Room से leave करते हैं
            leave_room(room_code)
            
            # Rooms dictionary से remove करते हैं
            if room_code in rooms and socket_id in rooms[room_code]:
                rooms[room_code].remove(socket_id)
                
                # अगर room empty हो गया, तो delete कर देते हैं
                if len(rooms[room_code]) == 0:
                    del rooms[room_code]
                    print(f"[INFO] Room {room_code} deleted (empty)")
            
            print(f"[INFO] Client left room {room_code}. Socket ID: {socket_id}")
            
            # Success confirmation
            emit('leave_room_success', {
                'message': f'Room {room_code} se successfully leave ho gaya!',
                'room_code': room_code,
                'status': 'ok'
            })
            
            # Same room के बाकी clients को notify करते हैं
            if room_code in rooms:
                socketio_instance.emit('room_update', {
                    'message': 'Ek client ne room leave kiya',
                    'room_code': room_code,
                    'total_clients': len(rooms[room_code]),
                    'status': 'ok'
                }, room=room_code)
                
        except Exception as e:
            print(f"[ERROR] Error in leave_room: {e}")
            emit('leave_room_error', {
                'message': f'Error: {str(e)}',
                'status': 'error'
            })
    
    @socketio_instance.on('get_room_status')
    def handle_get_room_status(data):
        """
        Room की current status get करने के लिए
        
        Expected data format:
        {
            "code": "123456"  # 6-digit room code
        }
        """
        try:
            room_code = data.get('code', '').strip()
            
            if not room_code:
                emit('room_status_error', {
                    'message': 'Room code required!',
                    'status': 'error'
                })
                return
            
            # Room status return करते हैं
            if room_code in rooms:
                emit('room_status', {
                    'room_code': room_code,
                    'total_clients': len(rooms[room_code]),
                    'clients': rooms[room_code],
                    'exists': True,
                    'status': 'ok'
                })
            else:
                emit('room_status', {
                    'room_code': room_code,
                    'total_clients': 0,
                    'clients': [],
                    'exists': False,
                    'status': 'ok'
                })
                
        except Exception as e:
            print(f"[ERROR] Error in get_room_status: {e}")
            emit('room_status_error', {
                'message': f'Error: {str(e)}',
                'status': 'error'
            })
    
    @socketio_instance.on('disconnect')
    def handle_disconnect_cleanup():
        """
        जब client disconnect होता है, automatically सभी rooms से remove करते हैं
        """
        socket_id = request.sid
        
        # सभी rooms में से इस socket_id को remove करते हैं
        rooms_to_cleanup = []
        for room_code, clients in rooms.items():
            if socket_id in clients:
                clients.remove(socket_id)
                rooms_to_cleanup.append(room_code)
                
                # अगर room empty हो गया, तो delete कर देते हैं
                if len(clients) == 0:
                    del rooms[room_code]
                    print(f"[INFO] Room {room_code} deleted (client disconnected)")
                else:
                    # बाकी clients को notify करते हैं
                    socketio_instance.emit('room_update', {
                        'message': 'Ek client disconnect ho gaya',
                        'room_code': room_code,
                        'total_clients': len(clients),
                        'status': 'ok'
                    }, room=room_code)
        
        if rooms_to_cleanup:
            print(f"🧹 Cleaned up socket {socket_id} from {len(rooms_to_cleanup)} room(s)")

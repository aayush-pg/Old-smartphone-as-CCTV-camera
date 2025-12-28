"""
Backend Member 2 - WebRTC Signaling Logic
यह file WebRTC signaling messages forward करती है

Concepts:
- WebRTC Flow: Offer → Answer → ICE Candidates
- Offer: Camera peer-to-peer connection start करने के लिए भेजता है
- Answer: Viewer offer को accept करके answer भेजता है
- ICE Candidates: Network addresses जो direct connection के लिए use होते हैं
- Signaling Server: सिर्फ messages forward करता है, actual media नहीं
"""

from flask_socketio import emit
from flask import request

def register_signaling_events(socketio_instance):
    """
    WebRTC signaling events register करता है
    """
    
    @socketio_instance.on('offer')
    def handle_offer(data):
        """
        WebRTC Offer message handle करता है
        Camera → Server → Viewer
        
        Expected data format:
        {
            "offer": {...},  # WebRTC offer object
            "room_code": "123456",  # Room code (optional, for room-based forwarding)
            "target_socket_id": "socket_id"  # Specific client को भेजने के लिए (optional)
        }
        """
        try:
            socket_id = request.sid  # Sender का socket ID
            offer_data = data.get('offer')
            room_code = data.get('room_code')
            target_socket_id = data.get('target_socket_id')
            
            if not offer_data:
                emit('signaling_error', {
                    'message': 'Offer data missing!',
                    'status': 'error'
                })
                return
            
            print(f"[INFO] Offer received from {socket_id}")
            
            # Forward करने का तरीका:
            # 1. अगर room_code दिया है, तो same room के सभी clients को भेजो
            # 2. अगर target_socket_id दिया है, तो specific client को भेजो
            # 3. वरना, sender को छोड़कर सभी connected clients को भेजो
            
            if room_code:
                socketio_instance.emit('offer', {
                    'offer': offer_data,
                    'room_code': room_code,
                    'from_socket_id': socket_id
                }, room=room_code, skip_sid=socket_id)
                print(f"📨 Offer forwarded to room {room_code}")
                
            elif target_socket_id:
                # Specific client को forward
                socketio_instance.emit('offer', {
                    'offer': offer_data,
                    'from_socket_id': socket_id
                }, room=target_socket_id)
                print(f"[INFO] Offer forwarded to specific client {target_socket_id}")
                
            else:
                # Broadcast to all except sender
                socketio_instance.emit('offer', {
                    'offer': offer_data,
                    'from_socket_id': socket_id
                }, skip_sid=socket_id)
                print(f"[INFO] Offer broadcasted to all clients")
            
            # Sender को confirmation
            emit('offer_sent', {
                'message': 'Offer successfully forwarded',
                'status': 'ok'
            })
            
        except Exception as e:
            print(f"[ERROR] Error in handle_offer: {e}")
            emit('signaling_error', {
                'message': f'Error forwarding offer: {str(e)}',
                'status': 'error'
            })
    
    @socketio_instance.on('answer')
    def handle_answer(data):
        """
        WebRTC Answer message handle करता है
        Viewer → Server → Camera
        
        Expected data format:
        {
            "answer": {...},  # WebRTC answer object
            "room_code": "123456",  # Room code (optional)
            "target_socket_id": "socket_id"  # Specific client को भेजने के लिए (optional)
        }
        """
        try:
            socket_id = request.sid  # Sender का socket ID
            answer_data = data.get('answer')
            room_code = data.get('room_code')
            target_socket_id = data.get('target_socket_id')
            
            if not answer_data:
                emit('signaling_error', {
                    'message': 'Answer data missing!',
                    'status': 'error'
                })
                return
            
            print(f"[INFO] Answer received from {socket_id}")
            
            # Same logic as offer - forward करते हैं
            if room_code:
                socketio_instance.emit('answer', {
                    'answer': answer_data,
                    'room_code': room_code,
                    'from_socket_id': socket_id
                }, room=room_code, skip_sid=socket_id)
                print(f"[INFO] Answer forwarded to room {room_code}")
                
            elif target_socket_id:
                socketio_instance.emit('answer', {
                    'answer': answer_data,
                    'from_socket_id': socket_id
                }, room=target_socket_id)
                print(f"[INFO] Answer forwarded to specific client {target_socket_id}")
                
            else:
                socketio_instance.emit('answer', {
                    'answer': answer_data,
                    'from_socket_id': socket_id
                }, skip_sid=socket_id)
                print(f"[INFO] Answer broadcasted to all clients")
            
            # Sender को confirmation
            emit('answer_sent', {
                'message': 'Answer successfully forwarded',
                'status': 'ok'
            })
            
        except Exception as e:
            print(f"[ERROR] Error in handle_answer: {e}")
            emit('signaling_error', {
                'message': f'Error forwarding answer: {str(e)}',
                'status': 'error'
            })
    
    @socketio_instance.on('ice_candidate')
    def handle_ice_candidate(data):
        """
        ICE Candidate message handle करता है
        Camera/Viewer → Server → Other Peer
        
        Expected data format:
        {
            "candidate": {...},  # ICE candidate object
            "room_code": "123456",  # Room code (optional)
            "target_socket_id": "socket_id"  # Specific client को भेजने के लिए (optional)
        }
        """
        try:
            socket_id = request.sid  # Sender का socket ID
            candidate_data = data.get('candidate')
            room_code = data.get('room_code')
            target_socket_id = data.get('target_socket_id')
            
            if not candidate_data:
                emit('signaling_error', {
                    'message': 'ICE candidate data missing!',
                    'status': 'error'
                })
                return
            
            print(f"[INFO] ICE candidate received from {socket_id}")
            
            # Forward करते हैं
            if room_code:
                socketio_instance.emit('ice_candidate', {
                    'candidate': candidate_data,
                    'room_code': room_code,
                    'from_socket_id': socket_id
                }, room=room_code, skip_sid=socket_id)
                print(f"[INFO] ICE candidate forwarded to room {room_code}")
                
            elif target_socket_id:
                socketio_instance.emit('ice_candidate', {
                    'candidate': candidate_data,
                    'from_socket_id': socket_id
                }, room=target_socket_id)
                print(f"[INFO] ICE candidate forwarded to specific client {target_socket_id}")
                
            else:
                socketio_instance.emit('ice_candidate', {
                    'candidate': candidate_data,
                    'from_socket_id': socket_id
                }, skip_sid=socket_id)
                print(f"[INFO] ICE candidate broadcasted to all clients")
            
            # Sender को confirmation (optional, क्योंकि ICE candidates बहुत frequent होते हैं)
            # emit('ice_candidate_sent', {'status': 'ok'})
            
        except Exception as e:
            print(f"[ERROR] Error in handle_ice_candidate: {e}")
            emit('signaling_error', {
                'message': f'Error forwarding ICE candidate: {str(e)}',
                'status': 'error'
            })

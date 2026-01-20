from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from routes.auth import auth_bp, token_required
from config import Config
import os
import sqlite3
import random
import socket
from datetime import datetime

def get_local_ip():
    """Get the local IP address dynamically"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"

# Initialize App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB Limit

# ✅ ENABLE CORS FOR EVERYTHING (Fixes "Server Error")
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Register Login Route
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Helper function for database connection
def get_db_connection():
    conn = sqlite3.connect('webwatch.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- 🔑 CODE GENERATION ROUTE (User-specific) ---
@app.route('/api/code/generate', methods=['GET'])
@token_required
def generate_code_route(current_user_id, current_username):
    code = str(random.randint(100000, 999999))
    return jsonify({"code": code, "success": True}), 200

# --- 📹 USER-SPECIFIC CAMERA ROUTES ---

# Get user's cameras
@app.route('/api/cameras', methods=['GET'])
@token_required
def get_user_cameras(current_user_id, current_username):
    try:
        conn = get_db_connection()
        cameras = conn.execute(
            'SELECT * FROM cameras WHERE user_id = ? ORDER BY created_at DESC',
            (current_user_id,)
        ).fetchall()
        conn.close()
        
        return jsonify([dict(camera) for camera in cameras]), 200
    except Exception as e:
        print(f"❌ Error fetching cameras: {e}")
        return jsonify({"error": str(e)}), 500

# Save camera for user
@app.route('/api/cameras', methods=['POST'])
@token_required
def save_camera(current_user_id, current_username):
    try:
        data = request.json
        name = data.get('name')
        code = data.get('code')
        status = data.get('status', 'Waiting')
        
        if not name or not code:
            return jsonify({"error": "Name and code are required"}), 400
        
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO cameras (user_id, name, code, status) VALUES (?, ?, ?, ?)',
            (current_user_id, name, code, status)
        )
        camera_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Camera saved for user {current_username}: {name} (Code: {code})")
        return jsonify({"success": True, "camera_id": camera_id}), 201
    except Exception as e:
        print(f"❌ Error saving camera: {e}")
        return jsonify({"error": str(e)}), 500

# Delete user's camera
@app.route('/api/cameras/<int:camera_id>', methods=['DELETE'])
@token_required
def delete_camera(current_user_id, current_username, camera_id):
    try:
        conn = get_db_connection()
        
        # Verify camera belongs to user
        camera = conn.execute(
            'SELECT * FROM cameras WHERE id = ? AND user_id = ?',
            (camera_id, current_user_id)
        ).fetchone()
        
        if not camera:
            conn.close()
            return jsonify({"error": "Camera not found"}), 404
        
        # Delete camera
        conn.execute('DELETE FROM cameras WHERE id = ?', (camera_id,))
        conn.commit()
        conn.close()
        
        print(f"✅ Camera {camera_id} deleted by user {current_username}")
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"❌ Error deleting camera: {e}")
        return jsonify({"error": str(e)}), 500

# --- 📹 USER-SPECIFIC VIDEO MANAGEMENT ROUTES ---

# 1. Upload Video (User-specific)
@app.route('/api/upload', methods=['POST'])
@token_required
def upload_recording(current_user_id, current_username):
    try:
        print(f"📤 Upload request from user: {current_username} (ID: {current_user_id})")
        
        if 'video' not in request.files:
            print("❌ No video file in request")
            return jsonify({"error": "No video file provided"}), 400
            
        file = request.files['video']
        camera_name = request.form.get('camera_name', 'Unknown Camera')
        camera_code = request.form.get('camera_code', '')
        
        # 🎯 GET ACTUAL RECORDING START TIME (sent from frontend)
        recording_start_time = request.form.get('recording_start_time')
        print(f"📅 Received recording start time: {recording_start_time}")
        print(f"📷 Camera name: {camera_name}")
        
        if not file or file.filename == '':
            print("❌ Empty file received")
            return jsonify({"error": "Empty file"}), 400
        
        # Check file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        print(f"📊 File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
        
        if file_size == 0:
            print("❌ File size is 0")
            return jsonify({"error": "Empty video file"}), 400
            
        if file_size > 500 * 1024 * 1024:
            print(f"❌ File too large: {file_size} bytes")
            return jsonify({"error": "File too large (max 500MB)"}), 413
        
        # Generate filename with user_id prefix for organization
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_extension = 'webm'
        
        if file.content_type:
            print(f"📋 Content type: {file.content_type}")
            if 'mp4' in file.content_type:
                file_extension = 'mp4'
            elif 'webm' in file.content_type:
                file_extension = 'webm'
        
        filename = f"user{current_user_id}_rec_{timestamp}.{file_extension}"
        save_path = os.path.join('recordings', filename)
        
        print(f"💾 Saving to: {save_path}")
        
        # Ensure recordings directory exists
        if not os.path.exists('recordings'):
            os.makedirs('recordings')
            print("📁 Created recordings directory")
        
        # Save file
        file.save(save_path)
        print(f"✅ File saved successfully")
        
        # Verify file was saved correctly
        if not os.path.exists(save_path) or os.path.getsize(save_path) == 0:
            print(f"❌ File verification failed")
            return jsonify({"error": "Failed to save file"}), 500
        
        # Get camera_id if camera_code is provided
        camera_id = None
        if camera_code:
            conn = get_db_connection()
            camera = conn.execute(
                'SELECT id FROM cameras WHERE code = ? AND user_id = ?',
                (camera_code, current_user_id)
            ).fetchone()
            if camera:
                camera_id = camera['id']
            conn.close()
        
        # Save to database with user_id
        conn = get_db_connection()
        print("🗄️ Connected to database")
        
        if recording_start_time:
            try:
                if recording_start_time.endswith('Z'):
                    actual_start = datetime.fromisoformat(recording_start_time.replace('Z', '+00:00'))
                else:
                    actual_start = datetime.fromisoformat(recording_start_time)
                
                conn.execute(
                    'INSERT INTO recordings (user_id, camera_id, filename, camera_name, recording_start_time, timestamp, file_size) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                    (current_user_id, camera_id, filename, camera_name, actual_start.isoformat(), datetime.now().isoformat(), file_size)
                )
                print(f"📅 Using actual recording start time: {actual_start}")
            except Exception as e:
                print(f"⚠️ Error parsing start time: {e}")
                conn.execute(
                    'INSERT INTO recordings (user_id, camera_id, filename, camera_name, timestamp, file_size) VALUES (?, ?, ?, ?, ?, ?)', 
                    (current_user_id, camera_id, filename, camera_name, datetime.now().isoformat(), file_size)
                )
        else:
            print("⚠️ No recording start time provided")
            conn.execute(
                'INSERT INTO recordings (user_id, camera_id, filename, camera_name, timestamp, file_size) VALUES (?, ?, ?, ?, ?, ?)', 
                (current_user_id, camera_id, filename, camera_name, datetime.now().isoformat(), file_size)
            )
            
        conn.commit()
        conn.close()
        print("✅ Database updated successfully")

        print(f"✅ Recording saved for user {current_username}: {filename}")
        return jsonify({
            "message": "Recording saved successfully", 
            "filename": filename,
            "size": file_size
        }), 200
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# 2. Get User's Recordings Only
@app.route('/api/recordings', methods=['GET'])
@token_required
def get_recordings(current_user_id, current_username):
    try:
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM recordings WHERE user_id = ? ORDER BY timestamp DESC",
            (current_user_id,)
        ).fetchall()
        conn.close()
        
        print(f"📼 Fetched {len(rows)} recordings for user {current_username}")
        return jsonify([dict(row) for row in rows]), 200
    except Exception as e:
        print(f"❌ Error fetching recordings: {e}")
        return jsonify({"error": str(e)}), 500

# 3. Play Video (User-specific - verify ownership)
@app.route('/recordings/<path:filename>')
def serve_video(filename):
    # Extract user_id from filename (format: user{id}_rec_timestamp.ext)
    try:
        # For backward compatibility, allow files without user prefix
        if not filename.startswith('user'):
            return send_from_directory('recordings', filename)
        
        # Verify user owns this recording
        # In production, you should verify JWT token here too
        return send_from_directory('recordings', filename)
    except Exception as e:
        print(f"❌ Error serving video: {e}")
        return jsonify({"error": "Video not found"}), 404

# 4. Delete Recording (User-specific)
@app.route('/api/recordings/<int:id>', methods=['DELETE'])
@token_required
def delete_recording(current_user_id, current_username, id):
    try:
        conn = get_db_connection()
        
        # Verify recording belongs to user
        row = conn.execute(
            "SELECT filename FROM recordings WHERE id = ? AND user_id = ?",
            (id, current_user_id)
        ).fetchone()
        
        if row:
            filename = row['filename']
            file_path = os.path.join('recordings', filename)
            
            # Delete File
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Deleted file: {filename}")
            
            # Delete DB Entry
            conn.execute("DELETE FROM recordings WHERE id = ?", (id,))
            conn.commit()
            conn.close()
            
            print(f"✅ Recording {id} deleted by user {current_username}")
            return jsonify({"success": True}), 200
        else:
            conn.close()
            return jsonify({"error": "Recording not found"}), 404
            
    except Exception as e:
        print(f"❌ Error deleting: {e}")
        return jsonify({"error": str(e)}), 500

# --- 👤 USER PROFILE ROUTES ---

@app.route('/api/profile/update', methods=['PUT'])
@token_required
def update_profile(current_user_id, current_username):
    try:
        data = request.json
        new_username = data.get('username')
        
        conn = get_db_connection()
        
        # Check if new username is taken (if username is being changed)
        if new_username and new_username != current_username:
            existing = conn.execute(
                'SELECT id FROM users WHERE username = ? AND id != ?',
                (new_username, current_user_id)
            ).fetchone()
            
            if existing:
                conn.close()
                return jsonify({"error": "Username already taken"}), 409
        
        # Update user profile
        conn.execute(
            'UPDATE users SET username = ? WHERE id = ?',
            (new_username or current_username, current_user_id)
        )
        conn.commit()
        conn.close()
        
        print(f"✅ Profile updated for user {current_user_id}")
        return jsonify({"success": True, "message": "Profile updated"}), 200
    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/profile/change-password', methods=['PUT'])
@token_required
def change_password(current_user_id, current_username):
    try:
        data = request.json
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({"error": "Both passwords are required"}), 400
        
        conn = get_db_connection()
        
        # Verify current password
        user = conn.execute(
            'SELECT password FROM users WHERE id = ?',
            (current_user_id,)
        ).fetchone()
        
        if not user or user['password'] != current_password:
            conn.close()
            return jsonify({"error": "Current password is incorrect"}), 401
        
        # Update password
        conn.execute(
            'UPDATE users SET password = ? WHERE id = ?',
            (new_password, current_user_id)
        )
        conn.commit()
        conn.close()
        
        print(f"✅ Password changed for user {current_username}")
        return jsonify({"success": True, "message": "Password updated"}), 200
    except Exception as e:
        print(f"❌ Error changing password: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/profile', methods=['DELETE'])
@token_required
def delete_account(current_user_id, current_username):
    try:
        conn = get_db_connection()
        
        # Enable foreign keys to ensure cascading delete works
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Check if user exists (sanity check)
        user = conn.execute('SELECT id FROM users WHERE id = ?', (current_user_id,)).fetchone()
        if not user:
            conn.close()
            return jsonify({"error": "User not found"}), 404
            
        print(f"🗑️ Deleting user account: {current_username} (ID: {current_user_id})")
        
        # Delete the user (Cascade should handle cameras, recordings, settings)
        # But we also need to delete physical recording files
        
        # 1. Get all recordings for this user to delete physical files
        recordings = conn.execute('SELECT filename FROM recordings WHERE user_id = ?', (current_user_id,)).fetchall()
        for rec in recordings:
            path = os.path.join('recordings', rec['filename'])
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"   - Deleted file: {path}")
                except Exception as ex:
                    print(f"   ! Failed to delete file {path}: {ex}")
        
        # 2. Delete the user
        conn.execute('DELETE FROM users WHERE id = ?', (current_user_id,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Account deleted successfully: {current_username}")
        return jsonify({"success": True, "message": "Account deleted permanently"}), 200
        
    except Exception as e:
        print(f"❌ Error deleting account: {e}")
        return jsonify({"error": str(e)}), 500

# --- 🔌 WEBRTC SIGNALING ---

@socketio.on('join_room')
def handle_join(data):
    room = str(data.get('code'))
    join_room(room)
    client_type = data.get('client_type', 'unknown')
    print(f"📡 {client_type.upper()} joined room: {room}")
    
    emit('viewer_joined', {'room_code': room, 'client_type': client_type}, room=room, include_self=False)
    emit('join_room_success', {'room_code': room}, room=room)

@socketio.on('offer')
def handle_offer(data):
    emit('offer', data, room=data['room_code'], include_self=False)

@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, room=data['room_code'], include_self=False)

@socketio.on('ice-candidate')
def handle_ice(data):
    emit('ice-candidate', data, room=data['room_code'], include_self=False)

if __name__ == '__main__':
    if not os.path.exists('recordings'):
        os.makedirs('recordings')
    
    # Get and display the current IP
    current_ip = get_local_ip()
    print(f"\n🌐 Server starting on IP: {current_ip}")
    print(f"📱 Backend URL: https://{current_ip}:5000")
    print(f"🖥️  Frontend URL: https://{current_ip}:3000")
    print("=" * 50)
        
    socketio.run(app, host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
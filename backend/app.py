from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from routes.auth import auth_bp
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
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB Limit

# ✅ ENABLE CORS FOR EVERYTHING (Fixes "Server Error")
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Register Login Route
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# --- 🔑 CODE GENERATION ROUTE ---
@app.route('/api/code/generate', methods=['GET'])
def generate_code_route():
    code = str(random.randint(100000, 999999))
    return jsonify({"code": code, "success": True}), 200

# --- 📹 VIDEO MANAGEMENT ROUTES ---

# 1. Upload Video (Enhanced for Mobile)
@app.route('/api/upload', methods=['POST'])
def upload_recording():
    try:
        print("📤 Upload request received")
        
        if 'video' not in request.files:
            print("❌ No video file in request")
            return jsonify({"error": "No video file provided"}), 400
            
        file = request.files['video']
        camera_name = request.form.get('camera_name', 'Unknown Camera')
        
        # 🎯 GET ACTUAL RECORDING START TIME (sent from frontend)
        recording_start_time = request.form.get('recording_start_time')
        print(f"📅 Received recording start time: {recording_start_time}")
        print(f"📷 Camera name: {camera_name}")
        
        if not file or file.filename == '':
            print("❌ Empty file received")
            return jsonify({"error": "Empty file"}), 400
        
        # Check file size (limit to 100MB for mobile compatibility)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        print(f"📊 File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
        
        if file_size == 0:
            print("❌ File size is 0")
            return jsonify({"error": "Empty video file"}), 400
            
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            print(f"❌ File too large: {file_size} bytes")
            return jsonify({"error": "File too large (max 100MB)"}), 413
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_extension = 'webm'  # Default to webm
        
        # Try to detect file type from content
        if file.content_type:
            print(f"📋 Content type: {file.content_type}")
            if 'mp4' in file.content_type:
                file_extension = 'mp4'
            elif 'webm' in file.content_type:
                file_extension = 'webm'
        
        filename = f"rec_{timestamp}.{file_extension}"
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
            print(f"❌ File verification failed: exists={os.path.exists(save_path)}, size={os.path.getsize(save_path) if os.path.exists(save_path) else 0}")
            return jsonify({"error": "Failed to save file"}), 500
        
        # Save to database with ACTUAL recording start time
        conn = sqlite3.connect('webwatch.db')
        print("🗄️ Connected to database")
        
        if recording_start_time:
            # Use the actual recording start time sent from frontend
            try:
                # Convert ISO string to datetime for database
                # Handle different ISO formats
                if recording_start_time.endswith('Z'):
                    actual_start = datetime.fromisoformat(recording_start_time.replace('Z', '+00:00'))
                else:
                    actual_start = datetime.fromisoformat(recording_start_time)
                
                conn.execute('INSERT INTO recordings (filename, camera_name, recording_start_time, timestamp) VALUES (?, ?, ?, ?)', 
                           (filename, camera_name, actual_start.isoformat(), datetime.now().isoformat()))
                print(f"📅 Using actual recording start time: {actual_start}")
            except Exception as e:
                print(f"⚠️ Error parsing start time ({recording_start_time}): {e}")
                # Fallback to basic insertion
                conn.execute('INSERT INTO recordings (filename, camera_name, timestamp) VALUES (?, ?, ?)', 
                           (filename, camera_name, datetime.now().isoformat()))
        else:
            # Fallback to current time if no start time provided
            print("⚠️ No recording start time provided, using current time")
            conn.execute('INSERT INTO recordings (filename, camera_name, timestamp) VALUES (?, ?, ?)', 
                       (filename, camera_name, datetime.now().isoformat()))
            
        conn.commit()
        conn.close()
        print("✅ Database updated successfully")

        print(f"✅ Recording saved: {filename} ({file_size} bytes)")
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

# 2. Get List of Recordings
@app.route('/api/recordings', methods=['GET'])
def get_recordings():
    conn = sqlite3.connect('webwatch.db')
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM recordings ORDER BY timestamp DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows]), 200

# 3. Play Video
@app.route('/recordings/<path:filename>')
def serve_video(filename):
    return send_from_directory('recordings', filename)

# 4. 🗑️ DELETE RECORDING (The New Feature)
@app.route('/api/recordings/<int:id>', methods=['DELETE'])
def delete_recording(id):
    try:
        conn = sqlite3.connect('webwatch.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get filename to delete from disk
        row = cursor.execute("SELECT filename FROM recordings WHERE id = ?", (id,)).fetchone()
        
        if row:
            filename = row['filename']
            file_path = os.path.join('recordings', filename)
            
            # Delete File
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete DB Entry
            cursor.execute("DELETE FROM recordings WHERE id = ?", (id,))
            conn.commit()
            conn.close()
            return jsonify({"success": True}), 200
        else:
            conn.close()
            return jsonify({"error": "Not found"}), 404
            
    except Exception as e:
        print(f"Error deleting: {e}")
        return jsonify({"error": str(e)}), 500

# --- 🔌 WEBRTC SIGNALING ---

@socketio.on('join_room')
def handle_join(data):
    room = str(data.get('code'))
    join_room(room)
    client_type = data.get('client_type', 'unknown')  # 'mobile' or 'dashboard'
    print(f"📡 {client_type.upper()} joined room: {room}")
    
    # Notify the room that someone joined (for reconnection)
    # This helps mobile know when dashboard reconnects
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
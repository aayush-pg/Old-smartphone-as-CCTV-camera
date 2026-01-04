from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from routes.auth import auth_bp
import os
import sqlite3
import random
from datetime import datetime

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

# 1. Upload Video
@app.route('/api/upload', methods=['POST'])
def upload_recording():
    if 'video' not in request.files:
        return jsonify({"error": "No video file"}), 400
        
    file = request.files['video']
    camera_name = request.form.get('camera_name', 'Unknown Camera')
    
    if file:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"rec_{timestamp}.webm"
        
        save_path = os.path.join('recordings', filename)
        file.save(save_path)
        
        conn = sqlite3.connect('webwatch.db')
        conn.execute('INSERT INTO recordings (filename, camera_name) VALUES (?, ?)', (filename, camera_name))
        conn.commit()
        conn.close()

        return jsonify({"message": "Saved", "filename": filename}), 200

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
    emit('join_room_success', room=room)

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
        
    socketio.run(app, host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
import sqlite3
from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint("auth", __name__)

# Secret key for JWT tokens
SECRET_KEY = "your-secret-key-change-in-production"

def get_db_connection():
    conn = sqlite3.connect('webwatch.db')
    conn.row_factory = sqlite3.Row
    return conn

# Middleware to verify JWT token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
            current_username = data['username']
            
            # Pass user info to the route
            return f(current_user_id, current_username, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    
    return decorated

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and user['password'] == password:
        # Generate JWT token
        token = jwt.encode({
            'user_id': user['id'],
            'username': user['username'],
            'exp': datetime.utcnow() + timedelta(days=30)  # Token valid for 30 days
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            "status": "ok", 
            "message": "Login successful",
            "access_token": token,
            "user": {
                "id": user['id'],
                "username": user['username']
            }
        }), 200
    else:
        return jsonify({"status": "error", "error": "Invalid credentials"}), 401

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    
    # Validate input
    if not username or not password:
        return jsonify({"status": "error", "error": "Username and password are required"}), 400
    
    if len(username) < 3:
        return jsonify({"status": "error", "error": "Username must be at least 3 characters"}), 400
    
    if len(password) < 6:
        return jsonify({"status": "error", "error": "Password must be at least 6 characters"}), 400
    
    conn = get_db_connection()
    
    # Check if username already exists
    existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({"status": "error", "error": "Username already exists"}), 409
    
    # Insert new user
    try:
        cursor = conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                            (username, password))
        user_id = cursor.lastrowid
        
        # Create default settings for new user
        conn.execute('INSERT INTO user_settings (user_id) VALUES (?)', (user_id,))
        
        conn.commit()
        
        # Generate JWT token for auto-login after signup
        token = jwt.encode({
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, SECRET_KEY, algorithm="HS256")
        
        conn.close()
        print(f"✅ New user created: {username} (ID: {user_id})")
        
        return jsonify({
            "status": "ok", 
            "message": "Account created successfully",
            "access_token": token,
            "user": {
                "id": user_id,
                "username": username
            }
        }), 201
    except Exception as e:
        conn.close()
        print(f"❌ Signup error: {e}")
        return jsonify({"status": "error", "error": "Failed to create account"}), 500

@auth_bp.route("/verify", methods=["GET"])
@token_required
def verify_token(current_user_id, current_username):
    """Verify if token is still valid"""
    conn = get_db_connection()
    user = conn.execute('SELECT id, username, email FROM users WHERE id = ?', (current_user_id,)).fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "status": "ok",
            "user": {
                "id": user['id'],
                "username": user['username']
            }
        }), 200
    else:
        return jsonify({"status": "error", "error": "User not found"}), 404
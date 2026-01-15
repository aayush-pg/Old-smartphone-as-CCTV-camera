import sqlite3
from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__)

def get_db_connection():
    conn = sqlite3.connect('webwatch.db')
    conn.row_factory = sqlite3.Row
    return conn

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and user['password'] == password:
        return jsonify({"status": "ok", "message": "Login successful"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    
    # Validate input
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required"}), 400
    
    if len(username) < 3:
        return jsonify({"status": "error", "message": "Username must be at least 3 characters"}), 400
    
    if len(password) < 3:
        return jsonify({"status": "error", "message": "Password must be at least 3 characters"}), 400
    
    conn = get_db_connection()
    
    # Check if username already exists
    existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({"status": "error", "message": "Username already exists"}), 409
    
    # Insert new user
    try:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        print(f"✅ New user created: {username}")
        return jsonify({"status": "ok", "message": "Account created successfully"}), 201
    except Exception as e:
        conn.close()
        print(f"❌ Signup error: {e}")
        return jsonify({"status": "error", "message": "Failed to create account"}), 500
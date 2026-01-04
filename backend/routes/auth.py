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
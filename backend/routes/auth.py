from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    # sample: accept username/password (demo only)
    username = data.get("username")
    password = data.get("password")
    if username == "admin" and password == "password":
        return jsonify({"status": "ok", "token": "fake-jwt-token"}), 200
    return jsonify({"status": "error", "message": "invalid credentials"}), 401

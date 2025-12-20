from flask import Blueprint, jsonify

login_bp = Blueprint("login", __name__)

# Fake Login API - No logic yet, just returns status
@login_bp.route("/login", methods=["POST"])
def login():
    return jsonify({"status": "ok"})


from flask import Blueprint, jsonify, request

camera_bp = Blueprint("camera", __name__)

# Example: register camera (mobile client can POST stream info)
@camera_bp.route("/register", methods=["POST"])
def register_camera():
    body = request.json or {}
    camera_name = body.get("name")
    # just echo for now
    return jsonify({"status": "ok", "camera": camera_name}), 201

# Example: get status
@camera_bp.route("/status", methods=["GET"])
def camera_status():
    return jsonify({"status": "ok", "message": "no active streams"})

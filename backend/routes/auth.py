from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    password = data.get("password")
    if password == "123":
        return "Success"
    return "Failure"

from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__)

# Real Login API with hardcoded credentials
# HTTP Status Codes:
# 200 = Success (OK)
# 401 = Unauthorized (Wrong credentials)
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login API with hardcoded credentials:
    username = "admin"
    password = "123"
    
    Reads data from request.json (POST request body)
    Returns appropriate status code and JSON response
    """
    # Get data from request body (JSON)
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    
    # Check credentials (hardcoded for now)
    if username == "admin" and password == "123":
        # Success: Return 200 status code with success message
        return jsonify({
            "status": "ok",
            "message": "login successful"
        }), 200
    else:
        # Failure: Return 401 status code (Unauthorized)
        return jsonify({
            "status": "error",
            "message": "Invalid username or password"
        }), 401

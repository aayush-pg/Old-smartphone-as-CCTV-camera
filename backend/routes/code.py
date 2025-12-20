from flask import Blueprint, jsonify
import random

code_bp = Blueprint("code", __name__)

# Code Generator API - Generates random 6-digit code
# Used for OTP, pairing codes, etc.
@code_bp.route("/generate", methods=["GET"])
def generate_code():
    """
    Generate a random 6-digit code
    random.randint(100000, 999999) generates number between 100000 and 999999
    This ensures code is always exactly 6 digits
    """
    code = random.randint(100000, 999999)
    return jsonify({"code": str(code)})


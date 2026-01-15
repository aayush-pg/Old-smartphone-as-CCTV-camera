import os
import socket

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    # For development you can set CORS_ORIGINS="*" or "http://localhost:3000"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    
    # Dynamic IP detection
    @staticmethod
    def get_local_ip():
        """Get the local IP address dynamically"""
        try:
            # Connect to a remote server to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "localhost"
    
    # Backend base url for docs (used by frontend team)
    BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", f"https://{get_local_ip.__func__()}:5000")

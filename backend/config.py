import os

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    # For development you can set CORS_ORIGINS="*" or "http://localhost:3000"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    # Backend base url for docs (used by frontend team)
    BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:5000")

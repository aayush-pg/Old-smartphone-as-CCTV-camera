from flask import Flask
from flask_cors import CORS
from routes.auth import auth_bp
from routes.camera import camera_bp
import config

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config.Config)

    # Enable CORS: allow frontend host (for dev use '*' but better to restrict)
    CORS(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS")}})

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(camera_bp, url_prefix="/api/camera")

    @app.route("/")
    def home():
        return "Backend Running!"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

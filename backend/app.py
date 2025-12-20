from flask import Flask, render_template
from flask_cors import CORS
from routes.auth import auth_bp
from routes.camera import camera_bp
from routes.login import login_bp
from routes.code import code_bp
import config

# Socket.IO imports
from sockets.basic import init_socketio, register_basic_events
from sockets.rooms import register_room_events
from sockets.signaling import register_signaling_events

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config.Config)

    # Enable CORS: allow frontend to call backend APIs
    # CORS enables Cross-Origin Resource Sharing - browser security feature
    # Without CORS, frontend (localhost:3000) cannot call backend (localhost:5000)
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS")}})

    # Register blueprints (routes organized by feature)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(camera_bp, url_prefix="/api/camera")
    app.register_blueprint(code_bp, url_prefix="/api/code")
    app.register_blueprint(login_bp)  # Login route at /login (no prefix)

    # Root route - basic health check
    @app.route("/")
    def home():
        return "Backend Running!"
    
    # API Tester page - for testing APIs in browser
    @app.route("/test")
    def test_page():
        return render_template("test_api.html")
    
    # Socket.IO Tester page
    @app.route("/socket-test")
    def socket_test_page():
        return render_template("socket_test.html")
    
    # Initialize Socket.IO
    socketio = init_socketio(app)
    
    # Register all Socket.IO events
    register_basic_events(socketio)
    register_room_events(socketio)
    register_signaling_events(socketio)
    
    print("Socket.IO initialized and all events registered!")
    print("WebSocket server ready on ws://localhost:5000")

    return app, socketio

if __name__ == "__main__":
    app, socketio = create_app()
    # Use socketio.run() instead of app.run() for Socket.IO support
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)

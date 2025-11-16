from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    from backend.app.routes.task_routes import task_bp
    app.register_blueprint(task_bp)

    return app
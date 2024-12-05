from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from app.models import setup_database, load_user
from app.routes import blueprints  # Import blueprints list
import os

login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder="../static")
    CORS(app)
    app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key_for_local_dev")
    app.config["DB_FILE"] = os.environ.get("DB_FILE", "smartnest.db")
    app.config["DATA_DIR"] = os.environ.get("DATA_DIR", "data")

    # Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.user_loader(load_user)

    # Setup database
    setup_database()

    # Register blueprints dynamically
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app

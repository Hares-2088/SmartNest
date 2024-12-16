#This script is used to view the existing users in the database and add a default user if none exist.
from .auth import auth_bp
from .api import api_bp
from .dashboard import dashboard_bp

# List of all blueprints for easier registration
blueprints = [auth_bp, api_bp, dashboard_bp]

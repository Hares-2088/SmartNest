from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from app.models import load_user
from app.utils import validate_password
import sqlite3
import os

auth_bp = Blueprint("auth", __name__)

DB_FILE = os.environ.get("DB_FILE", "smartnest.db")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Retrieve form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Connect to the database and fetch user info
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        # Validate credentials
        if user:
            user_id, db_username, hashed_password = user
            if validate_password(hashed_password, password):
                user_obj = load_user(user_id)
                login_user(user_obj)
                return redirect(url_for("dashboard.dashboard"))  # Redirect to the dashboard
            else:
                flash("Invalid password. Please try again.", "danger")
        else:
            flash("User does not exist. Please register.", "danger")

    # Render the login template
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Use the `add_user` function from `models.py`
        try:
            add_user(username, password)
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
        except sqlite3.IntegrityError:
            flash("Username already exists. Please choose a different one.", "danger")

    return render_template("register.html")

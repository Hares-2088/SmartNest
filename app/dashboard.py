from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
import os
import json
from datetime import datetime
from app.utils import calculate_stats

dashboard_bp = Blueprint("dashboard", __name__)

DATA_DIR = os.environ.get("DATA_DIR", "data")
if not os.path.exists(DATA_DIR):
    raise FileNotFoundError(f"Data directory {DATA_DIR} does not exist")

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Renders the dashboard page for the logged-in user.
    Displays the user's name and navigation links.
    """
    return render_template("dashboard.html", username=current_user.username)

@dashboard_bp.route("/stats")
@login_required
def stats():
    """
    Renders the stats page with daily, weekly, and monthly usage statistics.
    Statistics are calculated from JSON files in the `DATA_DIR` directory.
    """
    stats_data = calculate_stats()
    return render_template("stats.html", stats=stats_data)

@dashboard_bp.route("/plots")
@login_required
def plots():
    """
    Renders the plots page with data visualizations.
    Data is gathered from JSON files in the `DATA_DIR` directory.
    """
    plot_data = []

    # Read JSON files and gather data for plotting
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            try:
                file_date = filename.split(".")[0]  # Extract the date from the filename
                file_path = os.path.join(DATA_DIR, filename)
                with open(file_path, "r") as f:
                    data = json.load(f)
                    daily_usage = sum(item["usage"] for item in data)
                    plot_data.append({"date": file_date, "usage": daily_usage})
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file {filename}: {e}")
            except Exception as e:
                print(f"Error reading file {filename}: {e}")

    # Sort data by date for proper plotting
    plot_data.sort(key=lambda x: x["date"])

    # Pass plot data to the template
    return render_template("plots.html", plot_data=plot_data)

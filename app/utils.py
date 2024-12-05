from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime, timedelta

DATA_DIR = os.environ.get("DATA_DIR", "data")

def hash_password(plain_password):
    return generate_password_hash(plain_password, method="sha256")

def validate_password(stored_password, provided_password):
    """Validate the provided password against the stored hashed password."""
    return check_password_hash(stored_password, provided_password)

def calculate_stats():
    total_daily, total_weekly, total_monthly = 0, 0, 0
    today = datetime.now()
    past_week = today - timedelta(days=7)
    past_month = today - timedelta(days=30)

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            try:
                file_date = datetime.strptime(filename.split(".")[0], "%Y-%m-%d")
                file_path = os.path.join(DATA_DIR, filename)
                if os.path.isfile(file_path):
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        if isinstance(data, list):  # Ensure data is in list format
                            daily_usage = sum(item.get("usage", 0) for item in data)
                            if file_date.date() == today.date():
                                total_daily += daily_usage
                            if file_date.date() >= past_week.date():
                                total_weekly += daily_usage
                            if file_date.date() >= past_month.date():
                                total_monthly += daily_usage
            except (ValueError, json.JSONDecodeError) as e:
                print(f"Error processing file {filename}: {e}")
    return {
        "daily_usage": f"{total_daily} kWh",
        "weekly_usage": f"{total_weekly} kWh",
        "monthly_usage": f"{total_monthly} kWh",
    }


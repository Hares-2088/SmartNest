from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime, timedelta
import random
import platform

# Initialize Flask app
app = Flask(__name__, static_folder="static")
CORS(app)  # Enable CORS for API routes
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")  # Use env variable for security

# Configuration
DB_FILE = os.environ.get("DB_FILE", "smartnest.db")
DATA_DIR = os.environ.get("DATA_DIR", "data")
BROKER = os.environ.get("BROKER", "localhost")
PORT = int(os.environ.get("PORT", 1883))
TOPIC = "smartnest/led"

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Platform-based mocking
if platform.system() == "Windows":
    class MockDHT:
        def __init__(self):
            self._temperature = 25.0
            self._humidity = 50.0

        @property
        def temperature(self):
            self._temperature += random.uniform(-0.5, 0.5)
            return round(self._temperature, 1)

        @property
        def humidity(self):
            self._humidity += random.uniform(-1, 1)
            self._humidity = max(0, min(100, self._humidity))
            return round(self._humidity, 1)

    adafruit_dht = MockDHT()
    board = None

    class MockLED:
        def __init__(self):
            self.state = "OFF"

        def on(self):
            self.state = "ON"
            print("Mock LED ON")

        def off(self):
            self.state = "OFF"
            print("Mock LED OFF")

    LED = MockLED
    led = LED()
else:
    import adafruit_dht
    import board
    from gpiozero import LED
    dht_device = adafruit_dht.DHT22(board.D4)
    led = LED(17)
    
def calculate_stats():
    total_daily = 0
    total_weekly = 0
    total_monthly = 0

    # Get today's and past dates
    today = datetime.now()
    past_week = today - timedelta(days=7)
    past_month = today - timedelta(days=30)

    # Iterate over all files in the data directory
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            try:
                # Parse the date from the filename
                file_date = datetime.strptime(filename.split(".")[0], "%Y-%m-%d")
                file_path = os.path.join(DATA_DIR, filename)

                # Read the file and calculate usage
                if os.path.isfile(file_path):
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        daily_usage = sum(item["usage"] for item in data)

                        # Aggregate usage based on file date
                        if file_date.date() == today.date():
                            total_daily += daily_usage
                        if file_date.date() >= past_week.date():
                            total_weekly += daily_usage
                        if file_date.date() >= past_month.date():
                            total_monthly += daily_usage
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    return {
        "daily_usage": f"{total_daily} kWh",
        "weekly_usage": f"{total_weekly} kWh",
        "monthly_usage": f"{total_monthly} kWh"
    }


# MQTT Setup
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Message received: {msg.topic} -> {msg.payload.decode()}")
    if msg.topic == TOPIC:
        if msg.payload.decode().lower() == "on":
            led.on()
        elif msg.payload.decode().lower() == "off":
            led.off()

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
try:
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"MQTT connection failed: {e}")

# Database setup
def setup_database():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS objects (
            object_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    ''')
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("password123"))
        )
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    return redirect(url_for("dashboard"))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            login_user(User(id=user[0], username=user[1]))
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.")
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)

@app.route('/api/sensor')
@login_required
def get_sensor_data():
    try:
        temperature = dht_device.temperature if platform.system() != "Windows" else adafruit_dht.temperature
        humidity = dht_device.humidity if platform.system() != "Windows" else adafruit_dht.humidity
        return jsonify({"temperature": temperature, "humidity": humidity})
    except Exception as e:
        print(f"Sensor error: {e}")
        return jsonify({"error": "Unable to read sensor data"}), 500

@app.route('/api/led/<state>')
@login_required
def control_led(state):
    if state.lower() == "on":
        led.on()
        mqtt_client.publish(TOPIC, "ON")
        return jsonify({"status": "LED turned ON"})
    elif state.lower() == "off":
        led.off()
        mqtt_client.publish(TOPIC, "OFF")
        return jsonify({"status": "LED turned OFF"})
    return jsonify({"error": "Invalid LED state"}), 400

@app.route('/stats')
@login_required
def stats():
    # Use previously defined `calculate_stats` logic here
    stats_data = calculate_stats()
    return render_template("stats.html", stats=stats_data)

@app.route('/plots')
@login_required
def plots():
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
            except Exception as e:
                print(f"Error reading file {filename}: {e}")

    # Sort data by date for proper plotting
    plot_data.sort(key=lambda x: x["date"])

    # Pass plot data to the template
    return render_template("plots.html", plot_data=plot_data)


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(id=row[0], username=row[1])
    return None

# Initialize app
if __name__ == "__main__":
    setup_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
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

app = Flask(__name__)
CORS(app)  # Enable CORS for your Flask app

# Detect platform and mock adafruit_dht for Windows
if platform.system() == "Windows":
    class MockDHT:
        def __init__(self, *args, **kwargs):
            self._temperature = 25.0  # Start with 25°C
            self._humidity = 50.0     # Start with 50%

        @property
        def temperature(self):
            # Simulate slight temperature fluctuations
            self._temperature += random.uniform(-0.5, 0.5)
            return round(self._temperature, 1)

        @property
        def humidity(self):
            # Simulate slight humidity fluctuations
            self._humidity += random.uniform(-1, 1)
            self._humidity = max(0, min(100, self._humidity))  # Keep humidity between 0% and 100%
            return round(self._humidity, 1)

    adafruit_dht = MockDHT
    board = None
else:
    import adafruit_dht
    import board
    dht_device = adafruit_dht.DHT22(board.D4)  # Use GPIO pin 4 on Raspberry Pi

from gpiozero import LED
import paho.mqtt.client as mqtt

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configuration
DB_FILE = "smartnest.db"
DATA_DIR = "data"

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Detect platform and mock gpiozero for Windows
if platform.system() == "Windows":
    class MockLED:
        def __init__(self, *args, **kwargs):
            self.state = "OFF"  # Initial state is OFF

        def on(self):
            self.state = "ON"
            print("Mock LED ON")

        def off(self):
            self.state = "OFF"
            print("Mock LED OFF")

    LED = MockLED
else:
    from gpiozero import LED

# Initialize Components
led = LED(17)  # GPIO pin 17 for LED

# MQTT Configuration
BROKER = "localhost"
PORT = 1883
TOPIC = "smartnest/led"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Message received: {msg.topic} -> {msg.payload.decode()}")
    if msg.topic == "smartnest/led":
        if msg.payload.decode().lower() == "on":
            led.on()
        elif msg.payload.decode().lower() == "off":
            led.off()

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
            file_date = datetime.strptime(filename.split(".")[0], "%Y-%m-%d")
            file_path = os.path.join(DATA_DIR, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    daily_usage = sum(item["usage"] for item in data)

                    # Accumulate usage based on file date
                    if file_date.date() == today.date():
                        total_daily += daily_usage
                    if file_date.date() >= past_week.date():
                        total_weekly += daily_usage
                    if file_date.date() >= past_month.date():
                        total_monthly += daily_usage

    return {
        "daily_usage": f"{total_daily} kWh",
        "weekly_usage": f"{total_weekly} kWh",
        "monthly_usage": f"{total_monthly} kWh"
    }

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Load user function for Flask-Login
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

# Database setup
def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Objects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS objects (
            object_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    ''')
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Add an admin user if it doesn't exist
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("password123"))
        )
    conn.commit()
    conn.close()

# Helper to save daily sensor data to a file
def save_sensor_data_to_file(data):
    today = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(DATA_DIR, f"{today}.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    return file_path

# Helper to generate and save mock data
def generate_and_save_mock_data():
    data = []
    now = datetime.now()
    # Generate 24 hours of mock data with realistic variations
    for i in range(24):
        timestamp = (now - timedelta(hours=(24 - i))).strftime('%Y-%m-%d %H:%M:%S')
        usage = random.randint(10, 30)  # Simulate energy usage between 10 and 30 kWh
        data.append({"timestamp": timestamp, "usage": usage})

    # Save to today's JSON file
    file_path = save_sensor_data_to_file(data)
    return file_path, data

# Add object metadata to the database
def add_object_to_database(name, type, file_path):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO objects (name, type, file_path, last_updated)
        VALUES (?, ?, ?, ?)
    ''', (name, type, file_path, now))
    conn.commit()
    conn.close()

# Fetch all objects from the database
def get_all_objects():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM objects")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fetch sensor data (real on Pi, mock on Windows)
@app.route('/api/sensor')
@login_required
def get_sensor_data():
    try:
        if platform.system() == "Windows":
            dht_device = adafruit_dht()  # Mock DHT device
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        return jsonify({"temperature": temperature, "humidity": humidity})
    except RuntimeError as error:
        print(f"Sensor error: {error}")
        return jsonify({"error": "Unable to read sensor data"}), 500

# Control the LED via Flask route
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
    else:
        return jsonify({"error": "Invalid LED state"}), 400

# Flask Routes for web pages
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

@app.route('/stats')
@login_required
def stats():
    stats_data = calculate_stats()
    return render_template("stats.html", stats=stats_data)

@app.route('/plots')
@login_required
def plots():
    # Gather data for plots
    plot_data = []

    for filename in os.listdir(DATA_DIR):
        if os.path.isfile(os.path.join(DATA_DIR, filename)):
            file_date = filename.split(".")[0]  # Extract date from filename
            with open(os.path.join(DATA_DIR, filename), "r") as f:
                data = json.load(f)
                daily_usage = sum(item["usage"] for item in data)
                plot_data.append({"date": file_date, "usage": daily_usage})

    # Sort the data by date
    plot_data.sort(key=lambda x: x["date"])

    return render_template("plots.html", plot_data=plot_data)

# Initialize the database and add mock data on startup
if __name__ == '__main__':
    setup_database()
    # Add mock data for testing
    file_path, _ = generate_and_save_mock_data()
    add_object_to_database("Living Room Motion Sensor", "motion", file_path)
    add_object_to_database("Kitchen Temperature Sensor", "temperature", file_path)
    app.run(host='0.0.0.0', port=5000, debug=True)

import sqlite3
import os
from datetime import datetime

DB_FILE = os.environ.get("DB_FILE", "smartnest.db")

def setup_database():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create users table (already exists)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create sensor_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_sensor_data(temperature, humidity):
    """Save sensor data to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()  # Current timestamp
    cursor.execute(
        "INSERT INTO sensor_data (timestamp, temperature, humidity) VALUES (?, ?, ?)",
        (timestamp, temperature, humidity)
    )
    
    conn.commit()
    conn.close()
    print(f"Saved data: Temperature={temperature}, Humidity={humidity} at {timestamp}")

def fetch_all_sensor_data():
    """Fetch all sensor data from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sensor_data")
    rows = cursor.fetchall()
    
    conn.close()
    return rows

def load_user(user_id):
    """Load a user by ID."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    return user

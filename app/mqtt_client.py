import os
import json
import time
from datetime import datetime
from app.sensors import read_sensor
from app.mqtt_client import mqtt_client  # Assumes MQTT client is initialized elsewhere
from app.models import save_sensor_data


DATA_DIR = os.environ.get("DATA_DIR", "data")
OFFLINE_FILE = os.path.join(DATA_DIR, "offline_data.json")

def is_connected():
    """Check if the Raspberry Pi is connected to the internet."""
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)  # Google's public DNS
        return True
    except OSError:
        return False

def store_data_offline(data):
    """Store data in the offline file."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if os.path.exists(OFFLINE_FILE):
        with open(OFFLINE_FILE, "r") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_data.append(data)
    with open(OFFLINE_FILE, "w") as file:
        json.dump(existing_data, file)

def publish_offline_data():
    """Publish offline data when the internet is available."""
    if not os.path.exists(OFFLINE_FILE):
        return

    with open(OFFLINE_FILE, "r") as file:
        try:
            offline_data = json.load(file)
        except json.JSONDecodeError:
            offline_data = []

    for entry in offline_data:
        try:
            # Publish data to MQTT or database
            mqtt_client.publish("smartnest/sensor", json.dumps(entry))
        except Exception as e:
            print(f"Error publishing data: {e}")
            return  # Stop if publishing fails to retry later

    # If all data is successfully published, delete the offline file
    os.remove(OFFLINE_FILE)

def publish_sensor_data():
    """Read sensor data, save to DB, and publish if connected."""
    try:
        sensor_data = read_sensor()
        timestamped_data = {
            "timestamp": datetime.now().isoformat(),
            "temperature": sensor_data["temperature"],
            "humidity": sensor_data["humidity"]
        }

        # Save to database
        save_sensor_data(
            temperature=sensor_data["temperature"],
            humidity=sensor_data["humidity"]
        )

        if is_connected():
            # Publish data to MQTT
            mqtt_client.publish("smartnest/sensor", json.dumps(timestamped_data))
            print("Published sensor data:", timestamped_data)
        else:
            print("Stored data locally. No internet connection.")
    except Exception as e:
        print(f"Error reading or processing sensor data: {e}")

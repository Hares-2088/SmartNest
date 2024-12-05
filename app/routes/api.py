from flask import Blueprint, jsonify
from flask_login import login_required
from app.sensors import read_sensor  # Corrected function name
from app.led import control_led
from app.mqtt_client import mqtt_client

api_bp = Blueprint("api", __name__)

@api_bp.route("/api/sensor")
@login_required
def get_sensor_data_api():
    """
    Fetch sensor data from the DHT sensor and return as JSON.
    """
    try:
        data = read_sensor()  # Use the correct function from sensors.py
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/api/led/<state>")
@login_required
def control_led_api(state):
    """
    Control the LED state (ON/OFF) and publish the state to MQTT.
    """
    try:
        # Validate and control LED
        led_response = control_led(state)
        # Publish the LED state to MQTT
        mqtt_client.publish("smartnest/led", state.upper())
        return jsonify(led_response)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api_bp.route("/api/sensor-data", methods=["GET"])
@login_required
def get_all_sensor_data():
    """Fetch all sensor data from the database."""
    try:
        data = fetch_all_sensor_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

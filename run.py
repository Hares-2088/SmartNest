import os
import logging
from app import create_app

# Create the Flask app
app = create_app()

# Raspberry Pi Specific Configuration
def configure_logging():
    """Configure logging for production on Raspberry Pi."""
    logging.basicConfig(
        filename="/var/log/smartnest.log",  # Log file path
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
    )
    logging.info("SmartNest app started on Raspberry Pi.")

def check_mqtt_server():
    """Check if the MQTT server is reachable."""
    broker = os.environ.get("BROKER", "localhost")
    port = int(os.environ.get("PORT", 1883))
    try:
        import socket
        with socket.create_connection((broker, port), timeout=5):
            logging.info(f"MQTT server reachable at {broker}:{port}")
    except Exception as e:
        logging.error(f"MQTT server not reachable: {e}")
        raise RuntimeError(f"MQTT server not reachable at {broker}:{port}")

# Entry point
if __name__ == "__main__":
    # Check if running on Raspberry Pi
    if os.uname().sysname == "Linux" and "raspberrypi" in os.uname().nodename:
        configure_logging()
        logging.info("Running on Raspberry Pi.")
    else:
        logging.warning("Not running on Raspberry Pi. Ensure MQTT server is available.")

    # Check MQTT server availability
    try:
        check_mqtt_server()
    except RuntimeError as e:
        print(str(e))  # Output error to console for visibility
        exit(1)  # Exit if MQTT server is not reachable

    # Run the Flask app
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_ENV") == "development")

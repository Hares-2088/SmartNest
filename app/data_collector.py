import time
from mqtt_client import publish_sensor_data

if __name__ == "__main__":
    while True:
        publish_sensor_data()
        time.sleep(60)  # Run every 60 seconds

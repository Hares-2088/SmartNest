import os
import platform
import random
import time

# Mock or Real DHT Sensor Setup
if platform.system() == "Windows" or os.environ.get("VERCEL"):
    # Mock DHT Sensor for development
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

    dht_sensor = MockDHT()
else:
    # Real DHT Sensor
    import adafruit_dht
    import board

    dht_sensor = adafruit_dht.DHT11(board.D4)  # GPIO 4

def read_sensor():
    for _ in range(3):  # Retry up to 3 times
        try:
            temperature = dht_sensor.temperature
            humidity = dht_sensor.humidity
            return {"temperature": temperature, "humidity": humidity}
        except RuntimeError as e:
            print(f"Retrying sensor read: {e}")
            time.sleep(2)
    raise RuntimeError("Failed to read sensor after retries.")

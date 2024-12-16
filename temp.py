#this file is to test my connection to the DHT11 sensor and to see if I can get the temperature and humidity readings from it.
import adafruit_dht
import board
import time

dht_sensor = adafruit_dht.DHT11(board.D4)  # GPIO 4

while True:
    try:
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity
        print(f"Temperature: {temperature}, Humidity: {humidity}")
        time.sleep(2)
    except RuntimeError as e:
        print(f"Error: {e}")
        time.sleep(2)

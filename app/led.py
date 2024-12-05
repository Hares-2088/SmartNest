import os
from gpiozero import LED

if os.environ.get("VERCEL") or os.name == "nt":  # Mock environment
    class MockLED:
        def __init__(self):
            self.state = "OFF"

        def on(self):
            self.state = "ON"

        def off(self):
            self.state = "OFF"

    led = MockLED()
else:
    # Real LED using GPIO pin 17
    led = LED(17)

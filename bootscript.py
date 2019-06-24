from RPi.GPIO import setup, setmode, output, BCM, OUT, LOW, HIGH, setwarnings
import json

with open("/home/pi/TeerApp/TeerApp/config.json", 'r') as f:
    pins = json.load(f).values()
setmode(BCM)
setwarnings(False)
setup(pins, OUT)
output(pins, LOW)

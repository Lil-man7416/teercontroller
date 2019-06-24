#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/home/pi/TeerApp/TeerApp")

from TeerApp import socketio as socketio
from TeerApp import app as application
application.secret_key = '9af76ag75hs4fg'

if __name__ == "__main__":
    socketio.run(appliaction)

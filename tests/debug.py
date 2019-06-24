import json
from werkzeug.datastructures import MultiDict
import sys
sys.path.insert(0, "/home/pi/TeerApp/TeerApp/src")
import ControllerHub
import RequestParser
from multiprocessing.managers import BaseManager
import multiprocessing


class ControllerManager(BaseManager):
    pass
#
#
# controllerhub = ControllerHub.ControllerHub()
# manager_server = ControllerManager(address=('', 5000), authkey=b'T5sxQvvg2l')
# manager_server.register('ControllerHub', callable=lambda: controllerhub)
# server = manager_server.get_server()
#
#
# def serve():
#     server.serve_forever()
#
#
# multiprocessing.Process(target=serve).start()
#
manager_client = ControllerManager(address=('127.0.0.1', 5000), authkey=b'T5sxQvvg2l')
manager_client.register('ControllerHub')
manager_client.connect()
ch = manager_client.ControllerHub()

with open("./tests/request_data.json", "r") as f:
    request_data = MultiDict(json.load(f))

with open("./tests/config.json", "r") as f:
    ports = json.load(f)

rp = RequestParser.RequestParser(request_data, ports)

ch.add_measurement(rp)


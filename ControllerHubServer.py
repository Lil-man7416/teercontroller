#!/usr/bin/python
from multiprocessing.managers import BaseManager
import sys
sys.path.insert(0, "/home/pi/TeerApp/TeerApp/src")
import ControllerHub

"""Manager server module provides the shared Controller class for the apache2 processes.
It is run by systemd. The configuration file can be found in /lib/systemd/system as manager_server.service.
"""


class ControllerManager(BaseManager):
    pass


ControllerHub = ControllerHub.ControllerHub()
manager = ControllerManager(address=('', 5000), authkey=b'T5sxQvvg2l')
manager.register('ControllerHub', callable=lambda: ControllerHub)

server = manager.get_server()
server.serve_forever()

import sys
sys.path.insert(0, '/home/pi/TeerApp/teercontroller/teercontroller')
import PhaseController
import threading


class Measurement:
    def __init__(self, adc, manager, lock, storage, req):
        self._storage = storage
        self._request = req
        self.queue = manager.Queue()
        self.queue_thread = threading.Thread(target=self._store)
        self.kill_flag = manager.Event()
        self.not_running_flag = manager.Event()
        self.controller = PhaseController.PhaseController(adc, lock, self.kill_flag, self.not_running_flag, self.queue, req.evom, req.measurer, req.relays, req.phases)
        self.main_thread = threading.Thread(target=self.controller.run)
        self.id = self._storage.create_measurement(req)

    @property
    def request(self):
        return self._request

    @property
    def name(self):
        return self._request.name

    @property
    def description(self):
        return self._request.description

    @property
    def email(self):
        return self._request.email

    def start(self):
        self.main_thread.start()
        self.queue_thread.start()

    def stop(self):
        self.controller.kill()

    @property
    def is_alive(self):
        return self.main_thread.is_alive()

    def _store(self):
        while self.main_thread.is_alive():
            value = self.queue.get()
            if value == "force stop":
                self._storage.stop_measurement(self.id, natural=False)
                break
            if value == "natural stop":
                self._storage.stop_measurement(self.id, natural=True)
                break
            self._storage.add_data(self.id, value[0], value[1])

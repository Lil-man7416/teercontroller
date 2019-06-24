import PhaseController
import multiprocessing
import threading


class Measurement:
    def __init__(self, id_, controller, q, storage):
        assert isinstance(controller, PhaseController.PhaseController), controller

        self.id = id_
        self.controller = controller
        self.process = multiprocessing.Process(target=controller.run)
        self.queue = q
        self.queue_loop = threading.Thread(target=self._store)
        self.storage = storage

    def start(self):
        self.process.start()
        self.queue_loop.start()

    def stop(self):
        self.controller.kill()

    def force_stop(self):
        self.process.terminate()
        self.queue.put("end")

    @property
    def is_alive(self):
        return self.process.is_alive()

    def _store(self):
        while self.process.is_alive():
            value = self.queue.get()
            if value == "end":
                break
            self.storage.add_data(self.id, value)

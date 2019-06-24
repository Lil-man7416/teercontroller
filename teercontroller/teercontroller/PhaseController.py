import Phase
import Series
import Device
import Measurer
import multiprocessing
import time


# Relays:
# [
#     {
#         "gpio": 1,
#         "active": True
#     },
#     {
#         "gpio": 16,
#         "active": False
#     }
# ]

# Phases:
# [
#     {
#         "duration": 21,
#         "delay_between_series": 2,
#         "flow": 0,
#     },
#     {
#         "duration": 54,
#         "delay_between_series": 4,
#         "flow": 5,
#     }
# ]

# Measurer:
# {
#     "frequency": 30
#     "duration": 200
# }


class PhaseController:
    def __init__(self, adc, lock, kill_flag, not_running_flag, queue, evom, measurer, relays, phases):
        assert isinstance(evom, dict), evom
        assert isinstance(measurer, dict), measurer
        assert isinstance(relays, list) and all(isinstance(x, dict) for x in relays), relays
        assert isinstance(phases, list) and all(isinstance(x, dict) for x in phases), phases

        self.measurer = Measurer.Measurer(measurer["frequency"], measurer["duration"], adc)
        self.evom = Device.Device(evom["gpio"], logic=True, wait=evom["wait"])
        self.relays = [Device.Device(r["gpio"], active=r["active"], wait=r["wait"], logic=True) for r in relays]
        self.series = Series.Series(self.measurer, self.relays)
        self.kill_flag = kill_flag
        self.not_running_flag = not_running_flag

        self.phases = [Phase.Phase(p["duration"], p["delay_between_series"], self.evom, self.series, self.kill_flag, self.not_running_flag, lock, queue) for p in phases]
        self.start = -1

    @property
    def is_running(self):
        return not self.not_running_flag.is_set()

    @property
    def duration(self):
        return sum(p.duration for p in self.phases)

    def kill(self):
        if not self.is_running:
            return
        self.kill_flag.set()
        self.not_running_flag.wait()

    def run(self):
        self.start = time.time()
        for phase in self.phases:
            phase.run(self.start)
            if self.kill_flag.is_set():
                self.kill_flag.clear()
                self.not_running_flag.set()
                break

import Pin
import time


class Device(Pin.Pin):
    def __init__(self, gpio, active=True, position="OFF", logic=False, wait=0):
        assert isinstance(logic, bool), logic
        l = {"state": "LOW", "function": self.low}
        h = {"state": "HIGH", "function": self.high}
        self._positions = {"OFF": l, "ON": h} if logic else {"OFF": h, "ON": l}
        assert position in self._positions, position
        assert isinstance(wait, (int, float)), wait
        state = self._positions[position]["state"]
        Pin.Pin.__init__(self, gpio, active=active, state=state)

        self._position = position
        self.wait = wait

    @property
    def position(self):
        return self._position

    @property
    def is_on(self):
        return True if self._position == "ON" else False

    def on(self):
        self._position = "ON"
        self._positions["ON"]["function"]()
        time.sleep(self.wait)

    def off(self):
        self._position = "OFF"
        self._positions["OFF"]["function"]()

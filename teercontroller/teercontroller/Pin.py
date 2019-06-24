from RPi.GPIO import setmode, setup, output, input, HIGH, LOW, IN, OUT, BCM, setwarnings


class Pin:
    def __init__(self, gpio, active=True, direction="OUT", state="LOW"):
        directions = {"IN": IN, "OUT": OUT}
        states = {"LOW": self.low, "HIGH": self.high}

        assert isinstance(gpio, int), gpio
        assert isinstance(active, bool), active
        assert direction in directions, direction
        assert state in states, state

        self.gpio = gpio
        self.active = active

        setwarnings(False)
        setmode(BCM)
        setup(self.gpio, directions[direction])

        states[state]()

    @property
    def state(self):
        return input(self.gpio)

    def high(self):
        output(self.gpio, HIGH)

    def low(self):
        output(self.gpio, LOW)

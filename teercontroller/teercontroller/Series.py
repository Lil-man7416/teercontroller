import Measurer
import Device


class Series:
    def __init__(self, measurer, relays):
        assert isinstance(measurer, Measurer.Measurer), measurer
        assert isinstance(relays, list) and all(isinstance(x, Device.Device) for x in relays), relays

        self.measurer = measurer
        self.relays = relays

    def run(self):
        measured_values = []
        for relay in self.relays:
            if relay.active:
                relay.on()  # implicitly waiting
                value = self.measurer.measure_adc()
                measured_values.append(value)
                relay.off()

        return measured_values

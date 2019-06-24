import Adafruit_ADS1x15
import time


class Measurer:
    GAINS = {float(2 / 3): 6.144,
             1: 4.096,
             2: 2.048,
             4: 1.024,
             8: 0.512,
             16: 0.256}

    def __init__(self, frequency, duration, adc, gain=1):
        assert isinstance(frequency, (int, float)), frequency
        assert isinstance(duration, (int, float)), duration
        assert isinstance(adc, Adafruit_ADS1x15.ADS1115), adc
        assert gain in self.GAINS, gain

        self.duration = duration
        self.frequency = frequency
        self.adc = adc
        self.gain = gain

    @property
    def sampling_cycles(self):
        return int(round(self.duration / self.sampling_delay))  # s/s -> number of cycles

    @property
    def sampling_delay(self):
        return 1.0 / self.frequency  # Hz -> s

    def _convert(self, adc_value):
        return (adc_value / 2.0 ** 15 * self.GAINS[self.gain]) * 1000  # 1 ohm = 1mV

    def measure_adc(self):
        self.adc.start_adc(0, gain=self.gain)
        measurements = []
        for _ in range(self.sampling_cycles):
            measurements.append(self.adc.get_last_result())
            time.sleep(self.sampling_delay)
        self.adc.stop_adc()
        mean_value = sum(measurements) / float(len(measurements))
        return self._convert(int(mean_value))

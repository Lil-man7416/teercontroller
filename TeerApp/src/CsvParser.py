class CsvParser:
    def __init__(self, measurement, values):
        self._measurement = measurement
        self._values = values

    @property
    def measurement(self):
        return self._measurement

    @property
    def values(self):
        return self._values

    @property
    def metadata(self):
        duration = self.measurement['end_time'] - self.measurement['start_time'] if self.measurement['end_time'] else '???'
        result = "General information\r\n" \
                 "Measurement name: {measurement_name}\r\n" \
                 "Duration: {duration}\r\n" \
                 "Description: {description}\r\n\r\n" \
                 "Calibration parameters\r\n" \
                 "EVOM warmup time: {warmup}\r\n" \
                 "Series duration: {series_duration}\r\n" \
                 "Frequency: {frequency}\r\n" \
                 "Relay transient wait: {relay_wait}\r\n" \
                 "Active ports: {active_ports}\r\n\r\n" \
                 "Phases:\r\n".format(**self.measurement, duration=duration)

        for i, d in enumerate(self.measurement["phases"]):
            result += "#{}\r\n" \
                      "Duration: {duration}\r\n" \
                      "Delay between series: {delay_between_series}\r\n\r\n".format(i+1, **d)

        result += "===== VALUES START HERE =====\r\n\r\n"
        return result

    @property
    def values_text(self):
        result = "Time," + ",".join(self.measurement["active_ports"]) + "\r\n"
        for v in self.values:
            result += str(v["time"]) + "," + ",".join(["{:.1f}".format(x) for x in v["values"]]) + "\r\n"
        return result

    @property
    def full_text(self):
        return self.metadata + self.values_text

    @property
    def full_text_generator(self):
        return (x for x in self.full_text)

    @property
    def values_only_generator(self):
        return (x for x in self.values_text)

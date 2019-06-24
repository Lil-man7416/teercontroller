import Adafruit_ADS1x15
import multiprocessing
import Measurement
import RequestParser
import Storage
import datetime


class ControllerHub:
    def __init__(self):
        self.adc = Adafruit_ADS1x15.ADS1115()
        self.manager = multiprocessing.Manager()
        self.lock = self.manager.Lock()
        self.storage = Storage.Storage()
        self.measurement_list = []

    def add_measurement(self, request, autostart=True):
        assert isinstance(request, RequestParser.RequestParser), request

        measurement = Measurement.Measurement(self.adc, self.manager, self.lock, self.storage, request)
        self.measurement_list.append(measurement)
        if autostart:
            measurement.start()
        return measurement.id

    def stop_measurement(self, cid):
        assert isinstance(cid, int), cid
        measurement = self._find_measurement(cid)
        if measurement:
            measurement.stop()

    def _filter_running(self):
        result = filter(lambda x: not x.not_running_flag.is_set(), self.measurement_list)
        result = [x.id for x in result]
        return result

    def _predict_end_time(self, measurement):
        mult = {"sec": 1, "min": 60, "hour": 3600, "day": 86400}
        summa = 0
        for phase in measurement["phases"]:
            multiplier = mult[phase["duration"][1]]
            summa += phase["duration"][0] * multiplier
        return summa

    def get_running_measurements(self):
        result = self._filter_running()
        result = [self.storage.get_measurement(x) for x in result]
        for i in range(len(result)):
            result[i]["duration"] = datetime.timedelta(seconds=self._predict_end_time(result[i]))
        return result

    def get_running_measurement_with_values(self, id_):
        measurement = self.storage.get_measurement(id_)
        values = self.storage.get_values(id_)
        duration = datetime.timedelta(seconds=self._predict_end_time(measurement))
        return measurement, values, duration

    def get_finished_measurements(self):
        running = self._filter_running()
        all_measurements = self.storage.get_all_measurements()
        return [m for m in all_measurements if m["id"] not in running]

    def get_measurement_with_values(self, id_):
        measurement = self.storage.get_measurement(id_)
        values = self.storage.get_values(id_)
        return measurement, values

    def delete_measurement(self, id_):
        self.storage.delete_measurement(id_)

    def _find_measurement(self, cid):
        result = list(filter(lambda x: x.id == cid, self.measurement_list))
        return result[0] if result else None

    def get_all_measurements(self):
        return self.storage.get_all_measurements()

    def get_all_template_names(self):
        return self.storage.get_all_template_names()

    def add_template(self, request):
        return self.storage.add_template(request)

    def get_template(self, template_name):
        return self.storage.get_template(template_name)

    def delete_template(self, template_name):
        return self.storage.delete_template(template_name)


    # [
    #     {
    #         "id": 13543543,
    #         "controller": c
    #         "process": p
    #     },
    #     {
    #         "id": 13543543,
    #         "controller": c
    #         "process": p
    #     }
    # ]

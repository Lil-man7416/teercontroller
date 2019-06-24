from werkzeug.datastructures import MultiDict
import datetime


class RequestParser:
    def __init__(self, payload, ports):
        assert isinstance(payload, MultiDict), type(payload)
        assert isinstance(ports, dict), ports

        self.payload = payload
        self.ports = ports

    def is_template(self):
        return True if self.payload.get("save-template") is not None else False

    def is_delete(self):
        return True if self.payload.get("del-template") is not None else False

    @property
    def template_name(self):
        return self.payload.get("template_name", type=str)

    @property
    def measurement_name(self):
        return self.payload.get("measurement_name", type=str)

    @property
    def description(self):
        return self.payload.get("description", type=str)

    @property
    def user_email(self):
        return self.payload.get("user_email", type=str)

    @property
    def frequency(self):
        return self.payload.get("frequency", type=int)

    @property
    def series_duration(self):
        return self.payload.get("series_duration", type=int)

    @property
    def measurer(self):
        return dict(frequency=self.frequency,
                    duration=self.series_duration / 1000.0)

    @property
    def relays(self):
        assert len(self.active_ports) > 0, "No ports were selected"

        relay_list = [x for x in self.ports if x.startswith("port")]
        relay_list.sort()
        relays = []
        for r in relay_list:
            rd = dict(gpio=self.ports[r], active=(r in self.active_ports), wait=(self.relay_wait/1000.0))
            relays.append(rd)
        return relays

    @property
    def phases_raw(self):
        def get_order():
            result = self.payload.get('order', type=str).split(',')
            result.remove('')
            result = list(map(int, result))
            return result

        order = get_order()
        phases = []
        inputs = ['duration', 'delay_between_series']
        selects = ['duration_unit', 'delay_unit']

        for o in order:
            values_dict = {}
            for i, s in zip(inputs, selects):
                value = self.payload.get(i + str(o), type=float)  # keys stored as name + number. Eg.: flow2
                unit = self.payload.get(s + str(o), type=str)  # same as above eg.: duration_unit3
                values_dict[i] = (value, unit)
            phases.append(values_dict)
        return phases

    @property
    def phases(self):
        pre = self.phases_raw
        phases = []
        for phase in pre:
            temp = dict()
            for key in phase:
                tup = phase[key]
                temp[key] = self.convert(tup[0], tup[1])
            phases.append(temp)
        return phases

    @property
    def relay_wait(self):
        return self.payload.get("relay_wait", type=int)

    @property
    def warmup(self):
        return self.payload.get("warmup", type=int)

    @property
    def evom(self):
        return dict(gpio=self.ports["evom_port"],
                    wait=self.warmup / 1000.0)

    @property
    def active_ports(self):
        return sorted(list(set(self.payload) & set(self.ports)))

    def get_total_time(self):
        return sum(p["duration"] for p in self.phases)

    @staticmethod
    def convert(value, unit):
        ms = 0.001
        sec = 1
        min = 60  # shadows min(), but that's fine for now
        hour = 3600
        day = 86400
        return value * locals().get(unit, sec)

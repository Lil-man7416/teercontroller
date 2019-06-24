import psycopg2
import psycopg2.extras
from json import dumps
import datetime


class Storage:
    def __init__(self):
        self.connection = self.cursor = None
        try:
            self.connection = psycopg2.connect(
                dbname="teer",
                user="pi",
                host="localhost",
                password="asdf",
                port="5432"
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        except psycopg2.OperationalError:
            print("Could not connect to database")

    def create_measurement(self, request):
        sql = "INSERT INTO measurements(measurement_name, description, user_email, warmup, series_duration, frequency, relay_wait, active_ports, phases, start_time) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now())" \
                  "RETURNING id"
        r = request
        self.cursor.execute(sql, (r.measurement_name, r.description, r.user_email, r.warmup, r.series_duration, r.frequency, r.relay_wait, dumps(r.active_ports), dumps(r.phases_raw)))
        return self.cursor.fetchone()[0]

    def stop_measurement(self, id_, natural=True):
        sql = "UPDATE measurements SET natural_finish=%s, end_time=now() WHERE id=%s"
        self.cursor.execute(sql, (natural, id_))

    def delete_measurement(self, id_):
        sql = "DELETE FROM measurements WHERE id=%s"
        self.cursor.execute(sql, (id_,))
        return self.cursor.rowcount

    def get_measurement(self, id_):
        sql = "SELECT * FROM measurements WHERE id=%s"
        self.cursor.execute(sql, (id_,))
        return dict(self.cursor.fetchone())

    def get_all_measurements(self):
        sql = "SELECT * FROM measurements"
        self.cursor.execute(sql)
        return [dict(element) for element in self.cursor]

    def get_values(self, id_):
        sql = "SELECT time, values FROM sensor_data WHERE m_id=%s"
        self.cursor.execute(sql, (id_,))
        return [dict(element) for element in self.cursor]

    def add_data(self, m_id, t, values):
        sql = "INSERT INTO sensor_data (m_id, time, values) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (m_id, t, dumps(values)))

    def add_template(self, r):
        sql = "INSERT INTO templates( template_name, measurement_name, description, user_email, warmup, series_duration, frequency, relay_wait, active_ports, phases) " \
              "   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
              "   ON CONFLICT (template_name) DO UPDATE " \
              "   SET measurement_name = EXCLUDED.measurement_name, " \
              "       description = EXCLUDED.description, " \
              "       user_email = EXCLUDED.user_email, " \
              "       warmup = EXCLUDED.warmup, " \
              "       series_duration = EXCLUDED.series_duration, " \
              "       frequency = EXCLUDED.frequency, " \
              "       relay_wait = EXCLUDED.relay_wait, " \
              "       active_ports = EXCLUDED.active_ports, " \
              "       phases = EXCLUDED.phases; "

        self.cursor.execute(sql, (r.template_name,
                                  r.measurement_name,
                                  r.description,
                                  r.user_email,
                                  r.warmup,
                                  r.series_duration,
                                  r.frequency,
                                  r.relay_wait,
                                  dumps(r.active_ports),
                                  dumps(r.phases_raw)))


    def get_all_template_names(self):
        sql = "SELECT template_name FROM templates"
        self.cursor.execute(sql)
        return [dict(element) for element in self.cursor]

    def get_template(self, template_name):
        sql = "SELECT * FROM templates WHERE template_name=%s"
        self.cursor.execute(sql, (template_name,))
        return dict(self.cursor.fetchone())

    def delete_template(self, template_name):
        sql = "DELETE FROM templates WHERE template_name=%s"
        self.cursor.execute(sql, (template_name,))

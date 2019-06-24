#!/usr/bin/python3
from flask import Flask, render_template, request, Response, redirect, url_for
from flask_socketio import SocketIO
from multiprocessing.managers import BaseManager
import json
import sys
sys.path.insert(0, '/home/pi/TeerApp/TeerApp/src/')
import RequestParser
import CsvParser


class ControllerManager(BaseManager):
    pass


manager = ControllerManager(address=('127.0.0.1', 5000), authkey=b'T5sxQvvg2l')
manager.register('ControllerHub')
manager.connect()
ch = manager.ControllerHub()

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def homepage():
    return redirect(url_for("measurements"))


@app.route('/measurements/')
def measurements():
    running = ch.get_running_measurements()
    return render_template("measurements.html", measurements=running)


@app.route('/measurements/<int:identifier>')
def measurement(identifier):
    measurement, data, duration = ch.get_running_measurement_with_values(identifier)
    time_list = [x.get("time") for x in data]
    values = [[d["values"][x] for d in data] for x in range(len(measurement.get("active_ports")))]
    return render_template("measurement.html", measurement=measurement, time_list=time_list, values=values, duration=duration)


@app.route('/measurements/add', methods=['GET', 'POST'])
def add_measurement():
    if request.method == 'POST':
        with open("/home/pi/TeerApp/TeerApp/config.json", "r") as f:  # TODO: use relative path
            ports = json.load(f)
        parsed = RequestParser.RequestParser(request.form, ports)
        if parsed.is_template():
            ch.add_template(parsed)
            return redirect(url_for('load_template', template_name=parsed.template_name))
        if parsed.is_delete():
            ch.delete_template(parsed.template_name)
            return redirect(url_for('load_template', template_name="default"))
        ch.add_measurement(parsed)
        return redirect(url_for("measurements"))
    return redirect(url_for('load_template', template_name='default'))


@app.route('/measurements/add/load_template/<template_name>')
def load_template(template_name):
    names = [x["template_name"] for x in ch.get_all_template_names()]
    values = ch.get_template(template_name)
    return render_template('addmeasurement.html', template_names=names, values=values)


@app.route('/measurements/stop/<int:identifier>')
def stop_measurement(identifier):
    ch.stop_measurement(identifier)
    return redirect(url_for("measurements"))


@app.route('/results/')
def results():
    m = ch.get_finished_measurements()
    for i in range(len(m)):
        m[i]['duration'] = m[i]['end_time'] - m[i]['start_time'] if m[i]['end_time'] else '???'
    return render_template("results.html", measurements=m)


@app.route('/results/<int:identifier>')
def result(identifier):
    measurement, data = ch.get_measurement_with_values(identifier)
    time_list = [x.get("time") for x in data]
    values = [[d["values"][x] for d in data] for x in range(len(measurement.get("active_ports")))]
    duration = measurement['end_time'] - measurement['start_time'] if measurement['end_time'] else '???'
    return render_template("result.html", measurement=measurement, time_list=time_list, values=values, duration=duration)


@app.route('/results/get-csv/<int:identifier>')
def get_csv(identifier):
    m, v = ch.get_measurement_with_values(identifier)
    csv = CsvParser.CsvParser(m, v)
    gen = csv.full_text_generator if request.args.get("full") else csv.values_only_generator
    return Response(gen, mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename={}.txt".format(m["measurement_name"])})


@app.route('/results/delete/<int:identifier>')
def delete_result(identifier):
    ch.delete_measurement(identifier)
    return redirect(url_for("results"))


@app.route('/help')
def help_page():
    return render_template("help.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.html'), 404


if __name__ == "__main__":
    socketio.run(app)

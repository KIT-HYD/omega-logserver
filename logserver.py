from bottle import route, run, request, response, template, TEMPLATE_PATH, static_file, get
from datetime import datetime as dt
import json
import os

CONFIG = dict()

# don't know why we need this fix. bottle can't find the correct path...
TEMPLATE_PATH.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'views')))


@route('/')
def index():
    print()
    return template('index')


@route('/ping')
def ping():
    return {'acknowledged': True, 'host_ip': CONFIG.get('host_ip')}


@route('/id')
def dev_id():
    return CONFIG.get('dev_id')


@route('/acknowledge')
def acknowledge():
    return "1", 200


@route('/log', method=['POST', 'PUT'])
def log():
    data = request.json
    if data is None:
        response.status = 404
        return "404"
    else:
        save(data)
        response.status = 201
        return "201"


@route('/logs')
def logs():
    if not os.path.exists(CONFIG.get('logfile')):
        response.status = 405
        return "405"
    else:
        with open(CONFIG.get('logfile')) as logfile:
            logs = json.load(logfile)

    # get max and sort parameter
    total = len(logs)
    asc = request.params.get('asc', False)
    max_logs = request.params.get('max', total)

    # sorting
    ts = [dt.fromisoformat(log['time']).timestamp() for log in logs]
    logs = [logs[i] for i in [ts.index(_) for _ in sorted(ts, reverse=~asc)]]

    # limit the logs
    logs = logs[:max_logs]

    return {'found': len(logs), 'total': total, 'logs': logs}


@route('/devices', method=['GET'])
def devices():
    devices = device_journal()

    return {'found': len(devices.keys()), 'devices': devices}


def config(new_config=None):
    with open('config.json', 'r') as f:
        cur_config = json.load(f)
    if new_config is None:
        return cur_config
    else:
        cur_config.update(new_config)
        with open('config.json', 'w') as f:
            json.dump(cur_config, f)
            return cur_config


def save(payload):
    if os.path.exists(CONFIG.get('logfile')):
        with open(CONFIG.get('logfile'), 'r') as logfile:
            logs = json.load(logfile)
    else:
        logs = list()

    # build the log; TODO: put more metadata here...
    log = dict(time=str(dt.utcnow()), payload=payload)

    # append new data
    logs.append(log)

    with open(CONFIG.get('logfile'), 'w') as logfile:
        json.dump(logs, logfile, indent=4)


def device_journal(new_device):
    # load the journal
    if not os.path.exists('device_journal'):
        devices = dict()
    else:
        with open('device_journal.json', 'r') as jrn:
            devices = json.load(jrn)

    # return if needed
    if new_device is None:
        return devices

    # update
    else:
        devices.update(new_device)
        with open('device_journal.json', 'w') as jrn:
            json.dump(devices)


@get('/vendor/<filename>')
def vendor(filename):
    return static_file(filename=filename, root="vendor")


if __name__ == '__main__':
    CONFIG = config()

    run(host=CONFIG.get('host_ip'), port='5555', debug=True)

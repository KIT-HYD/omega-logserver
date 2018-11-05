from bottle import route, run, request, response, template, TEMPLATE_PATH, static_file, get
from datetime import datetime as dt
import json
import os

CONFIG = dict()
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
DTFMT = '%Y-%m-%d %H:%M:%S.%f'

# don't know why we need this fix. bottle can't find the correct path...
TEMPLATE_PATH.insert(0, os.path.join(BASE_PATH, 'views'))


@route('/')
def index():
    return static('index.html')
#    return template('index')


@route('/ping')
def ping():
    return {'acknowledged': True, 'host_ip': CONFIG.get('host_ip')}


@route('/id')
def dev_id():
    return CONFIG.get('dev_id')


@route('/acknowledge')
def acknowledge():
    return "1"


@route('/describe')
def describe():
    with open('VERSION') as v:
        version = v.read().strip()

    return dict(
        dev_id=CONFIG.get('dev_id'),
        host_ip=CONFIG.get('host_ip'),
        host_version=version
    )


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
        return {'found': 0, 'total': 0, 'logs': []}
    else:
        with open(CONFIG.get('logfile')) as logfile:
            logs = json.load(logfile)

    # get max and sort parameter
    total = len(logs)
    asc = bool(request.params.get('asc', False))
    max_logs = int(request.params.get('max', total))

    # sorting
    ts = [dt.strptime(log['time'], DTFMT).timestamp() for log in logs]
    logs = [logs[i] for i in [ts.index(_) for _ in sorted(ts, reverse=~asc)]]

    # limit the logs
    logs = logs[:max_logs]

    return {'found': len(logs), 'total': total, 'logs': logs}


@route('/devices', method=['GET'])
def devices():
    devices = device_journal()

    return {'found': len(devices.keys()), 'devices': [devices[dev_id] for dev_id in devices.keys()]}


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

    # append the new device
    device = parse_device(payload=payload)
    device_journal(new_device=device)
    if 'dev' in payload:
        del payload['dev']

    # build the log; TODO: put more metadata here...
    log = dict(time=str(dt.utcnow()), dev=device, payload=payload)

    # append new data
    logs.append(log)

    with open(CONFIG.get('logfile'), 'w') as logfile:
        json.dump(logs, logfile, indent=4)


def parse_device(payload):
    device = payload.get('dev', dict())
    dev_ip = request.remote_addr
    dev_id = device.get('dev_id', dev_ip)
    last = str(dt.utcnow())
    device.update(dict(dev_ip=dev_ip, dev_id=dev_id, last_connection=last))

    return device


def device_journal(new_device=None):
    # load the journal
    if not os.path.exists('device_journal.json'):
        devices = dict()
    else:
        with open('device_journal.json', 'r') as jrn:
            devices = json.load(jrn)

    # return if needed
    if new_device is None:
        return devices

    # update
    else:
        devices.update({new_device['dev_id']: new_device})
        with open('device_journal.json', 'w') as jrn:
            json.dump(devices, jrn, indent=4)


@get('/vendor/<filename>')
def vendor(filename):
    return static_file(filename=filename, root="vendor")


@get('/static/<filename>')
def static(filename):
    return static_file(filename=filename, root="views")


if __name__ == '__main__':
    os.chdir(BASE_PATH)
    CONFIG = config()

    run(host=CONFIG.get('host_ip'), port='5555', debug=True)

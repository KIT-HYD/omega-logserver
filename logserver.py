from bottle import route, run, request, response
from datetime import datetime as dt
import json
import os

CONFIG = dict()


@route('/')
def index():
    return "Hello World"


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

    return {'found': len(logs), 'logs': logs}


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


if __name__ == '__main__':
    CONFIG = config()

    run(host=CONFIG.get('host_ip'), port='5555', debug=True)

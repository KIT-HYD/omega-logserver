from bottle import route, run


@route('/')
def index():
    return "Hello World"


@route('/ping')
def ping():
    return {'acknowledged': True, 'host_id': 42}


run(host='127.0.0.1', port='5555', debug=True)

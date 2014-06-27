from pusher import Pusher
from application import app
from flask import request, jsonify, session

p = Pusher(
    app_id='79145',
    key='030e7fc986dac0c64bf4',
    secret='c1075e2abe140cc6aae2'
)


@app.route('/api/echo', methods=["GET", "POST"])
def test_message():
    data = request.form
    p['test_channel'].trigger('echo', {'message': data['message']})
    return jsonify({"status": 0})


num_users = 0


def emit(action, data, broadcast=False):
    if broadcast:
        print action, data
        p['br'].trigger(action, data)
    else:
        p[session['channel']].trigger(action, data)


@app.route('/api/call', methods=["GET", "POST"])
def api_call():
    data = request.form
    action_name = data["action"]
    if action_name == "add_user":
        add_user(data)
    elif True:
        pass
    else:
        pass

    return jsonify({"status": 0})


def add_user(data):
    global num_users
    session['username'] = data['username']
    session['user_id'] = data['user_id']
    session['channel'] = data['channel']
    num_users += 1

    emit('login', {
        'numUsers': num_users,
        'user_id': session['user_id'],
    })

    #WTF user joined fail...
    emit('user_joined', {
        'username': session['username'],
        'numUsers': num_users,
        'user_id': session['user_id'],
    }, broadcast=True)

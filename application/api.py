from pusher import Pusher
from application import app
from flask import request, jsonify, session
from pusher_info import pusher_app_id, pusher_key, pusher_secret

p = Pusher(
    app_id=pusher_app_id,
    key=pusher_key,
    secret=pusher_secret,
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
    eval("emit_" + action_name + "(data)")

    return jsonify({"status": 0})


def emit_add_user(data):
    global num_users
    session['username'] = data['username']
    session['user_id'] = data['user_id']
    session['channel'] = data['channel']
    num_users += 1

    emit('login', {
        'numUsers': num_users,
        'user_id': session['user_id'],
    })

    # WTF user joined fail...
    emit('user_joined', {
        'username': session['username'],
        'numUsers': num_users,
        'user_id': session['user_id'],
    }, broadcast=True)


def emit_del_user(data):
    global num_users

    if 'username' in session:
        num_users -= 1

        emit('user_left', {
            'username': session['username'],
            'numUsers': num_users,
            'user_id': session['user_id'],
        }, broadcast=True)


def emit_typing(data):
    emit('typing', {
        'username': session['username'],
        'user_id': session['user_id'],
    }, broadcast=True)


def emit_stop_typing(data):
    emit('stop_typing', {
        'username': session['username'],
        'user_id': session['user_id'],
    }, broadcast=True)


def emit_new_message(message):
    emit('new_message', {
        'username': session['username'],
        'message': message['message'],
        'user_id': session['user_id'],
    }, broadcast=True)

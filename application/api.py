from pusher import Pusher
from application import app, db
from flask import request, jsonify, session
from user_info import PUSHER_APP_ID, PUSHER_KEY, PUSHER_SECRET
from werkzeug.security import generate_password_hash, \
    check_password_hash
from models import (
    User
)

p = Pusher(
    app_id=PUSHER_APP_ID,
    key=PUSHER_KEY,
    secret=PUSHER_SECRET,
)

current_user = {}


def mark_online(username):
    current_user[username] = 0


@app.before_request
def mark_current_user_online():
    if 'username' in session:
        mark_online(session['username'])


@app.route('/api/echo', methods=["GET", "POST"])
def test_message():
    data = request.form
    p['test_channel'].trigger('echo', {'message': data['message']})
    return jsonify({"status": 0})


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
    nickname = data['username']
    password = "test"  # data['password']
    user = User.query.get(nickname)

    if user is None:
        user = User(nickname=nickname,
                    password=generate_password_hash(password)
                    )

        db.session.add(user)
        db.session.commit()
    elif not check_password_hash(user.password, password):
        #wrong
        #do nothing
        return "error"
    else:
        pass

    session['username'] = data['username']
    session['user_id'] = data['user_id']
    session['channel'] = data['channel']
    current_user[data['username']] = data['user_id']
    print current_user

    emit('login', {
        'numUsers': len(current_user),
        'user_id': session['user_id'],
    })

    # WTF user joined fail...
    emit('user_joined', {
        'username': session['username'],
        'numUsers': len(current_user),
        'user_id': session['user_id'],
    }, broadcast=True)


def emit_del_user(data):
    if 'username' in session:
        if session['username'] in current_user:
            current_user.pop(session['username'])

        emit('user_left', {
            'username': session['username'],
            'numUsers': len(current_user),
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

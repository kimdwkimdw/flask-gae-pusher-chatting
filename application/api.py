# -*- coding: utf-8 -*-
from pusher import Pusher
from application import app, db
from flask import request, jsonify, session
from user_info import PUSHER_APP_ID, PUSHER_KEY, PUSHER_SECRET
from werkzeug.security import generate_password_hash, \
    check_password_hash
from models import (
    User
)
import time

p = Pusher(
    app_id=PUSHER_APP_ID,
    key=PUSHER_KEY,
    secret=PUSHER_SECRET,
)

'''
사실 이런건 redis나 memcached로 해야하는데,
instance 한개만 띄우니까 일단 상관은 없
'''
current_user = {}


def get_number_of_current_user():
    now = int(time.time())
    for key in current_user.keys():
        if now - current_user[key] > 10:
            current_user.pop(key)

    return len(current_user)


def mark_online(username):
    now = int(time.time())
    current_user[username] = now


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


@app.route('/api/call/<action_name>', methods=["POST"])
def api_call(action_name):
    data = request.form
    methodname_to_call = "emit_" + action_name

    if methodname_to_call in globals():
        method_to_call = globals()[methodname_to_call]
        result = method_to_call(data)
    else:
        return jsonify({"status": -1, "message": "unknown action_name"})

    return jsonify({"status": 0})


@app.route('/api/trylogin', methods=["POST"])
def api_trylogin():
    data = request.form
    nickname = data['username']
    password = data['password']

    user = User.query.get(nickname)

    if user is None:
        user = User(nickname=nickname,
                    password=generate_password_hash(password)
                    )

        db.session.add(user)
        db.session.commit()
    elif not check_password_hash(user.password, password):
        # wrong
        # do nothing
        return jsonify({'status': -1})
    else:
        print "user found"

    session['username'] = data['username']
    session['user_id'] = data['user_id']
    session['channel'] = data['channel']

    current_user[data['username']] = int(time.time())

    # WTF user joined fail...
    emit('user_joined', {
        'username': session['username'],
        'numUsers': get_number_of_current_user(),
        'user_id': session['user_id'],
    }, broadcast=True)

    return jsonify({
        'status': 0,
        'numUsers': get_number_of_current_user(),
        'user_id': session['user_id'],
    })


def emit_del_user(data):
    if 'username' in session:
        if session['username'] in current_user:
            current_user.pop(session['username'])

        emit('user_left', {
            'username': session['username'],
            'numUsers': get_number_of_current_user(),
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

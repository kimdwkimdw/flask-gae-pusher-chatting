from pusher import Pusher
from application import app
from flask import request, jsonify

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

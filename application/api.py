import pusher

p = pusher.Pusher(
  app_id='79145',
  key='030e7fc986dac0c64bf4',
  secret='c1075e2abe140cc6aae2'
)

p['test_channel'].trigger('my_event', {'message': 'hello world'})
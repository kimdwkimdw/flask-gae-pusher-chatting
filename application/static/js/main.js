// Enable pusher logging - don't include this in production
Pusher.log = function(message) {
  if (window.console && window.console.log) {
    window.console.log(message);
  }
};

var pusher = new Pusher('030e7fc986dac0c64bf4');
var channel = pusher.subscribe('test_channel');
channel.bind('my_event', function(data) {
  alert(data.message);
});


setTimeout(function() {
  $.ajax({
    url: '/api/echo',
    data: {"message":"hello"},
  });
}, 2000);
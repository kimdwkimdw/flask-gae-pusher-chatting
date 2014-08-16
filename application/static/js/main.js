var SocketBinder = function(id) {
  var obj = {},
      callbacks = {};

  function emit(action, data) {
    data = data || {}
    data.channel = this.channel;
    $.post('/api/call/'+action, data);
  }

  function on(e, f) {
    callbacks[e] = f;
  }

  // Enable pusher logging - don't include this in production
  Pusher.log = function(message) {
    if (window.console && window.console.log) {
      window.console.log(message);
    }
  };

  var pusher = new Pusher(PUSHER_KEY);
  var channel = pusher.subscribe(id+"alksdjfajs");
  var broadcast = pusher.subscribe('br');

  pusher.bind_all(function(e, data) {
    if (e=="pong")
    {
      //default event
    } else {
      callbacks[e](data);  
    }
  });

  obj.emit = emit;
  obj.on = on;
  obj.channel = id+"alksdjfajs";
  return obj;
}

$(function() {
  var FADE_TIME = 150; // ms
  var TYPING_TIMER_LENGTH = 400; // ms
  var COLORS = [
    '#e21400', '#91580f', '#f8a700', '#f78b00',
    '#58dc00', '#287b00', '#a8f07a', '#4ae8c4',
    '#3b88eb', '#3824aa', '#a700ff', '#d300e7'
  ];

  // Initialize varibles
  var $window = $(window),
      $usernameInput = $('.usernameInput[name=username]'), // Input for username
      $passwordInput = $('.usernameInput[name=password]'), // Input for username
      $messages = $('.messages'), // Messages area
      $inputMessage = $('.inputMessage'), // Input message input box

      $loginPage = $('.login.page'), // The login page
      $chatPage = $('.chat.page'); // The chatroom page

  // Prompt for setting a username
  var username;
  var connected = false;
  var typing = false;
  var lastTypingTime;
  var $currentInput = $usernameInput.focus();

  var user_id = (function ()
    {
        var text = "";
        var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

        for( var i=0; i < 5; i++ )
            text += possible.charAt(Math.floor(Math.random() * possible.length));

        return text;
    })();

  var socket = SocketBinder(user_id);
  function addParticipantsMessage (data) {
    var message = '';
    if (data.numUsers === 1) {
      message += "there's 1 participant";
    } else {
      message += "there're " + data.numUsers + " participants";
    }
    log(message);
  }

  // Sets the client's username
  function setUsername () {
    var __username = cleanInput($usernameInput.val().trim());
    var __password = cleanInput($passwordInput.val().trim());

    // If the username is valid
    if (__username && __password) {
      // Tell the server your username
      $.ajax({
        type: "POST",
        url: "/api/trylogin",
        data: {'username':__username, 'password':__password, 'user_id': user_id,
        'channel': socket.channel},
        success: function(data) {
          console.log(data)

          if (data.status==0) {
            username = __username;
            $loginPage.fadeOut();
            $chatPage.show();
            $loginPage.off('click');
            $currentInput = $inputMessage.focus();

            connected = true;
            // Display the welcome message
            var message = "Welcome to Chat &mdash; ";
            log(message, {
              prepend: true
            });
            addParticipantsMessage(data);
          } else {
            alert("login fail: pasword wrong")
          }
        },
        dataType: "json"
      });
    } else {
      alert("not valid")
    }
  }

  // Sends a chat message
  function sendMessage () {
    var message = $inputMessage.val();
    // Prevent markup from being injected into the message
    message = cleanInput(message);
    // if there is a non-empty message and a socket connection
    if (message && connected) {
      $inputMessage.val('');
      addChatMessage({
        username: username,
        message: message
      });
      // tell server to execute 'new message' and send along one parameter
      socket.emit('new_message', {'message':message, 'user_id': user_id});
    }
  }

  // Log a message
  function log (message, options) {
    var el = '<li class="log">' + message + '</li>';
    addMessageElement(el, options);
  }

  // Adds the visual chat message to the message list
  function addChatMessage (data, options) {
    // Don't fade the message in if there is an 'X was typing'
    var $typingMessages = getTypingMessages(data);
    options = options || {};
    if ($typingMessages.length !== 0) {
      options.fade = false;
      $typingMessages.remove();
    }

    var colorStyle = 'style="color:' + getUsernameColor(data.username) + '"';
    var usernameDiv = '<span class="username"' + colorStyle + '>' +
      cleanInput(data.username) + '</span>';
    var messageBodyDiv = '<span class="messageBody">' +
      cleanInput(data.message) + '</span>';

    var typingClass = data.typing ? 'typing' : '';
    var messageDiv = '<li class="message ' + typingClass + '">' +
    usernameDiv + messageBodyDiv + '</li>';
    var $messageDiv = $(messageDiv).data('username', data.username);

    addMessageElement($messageDiv, options);
  }

  // Adds the visual chat typing message
  function addChatTyping (data) {
    data.typing = true;
    data.message = 'is typing';
    addChatMessage(data);
  }

  // Removes the visual chat typing message
  function removeChatTyping (data) {
    getTypingMessages(data).fadeOut(function () {
      $(this).remove();
    });
  }

  // Adds a message element to the messages and scrolls to the bottom
  // el - The element to add as a message
  // options.fade - If the element should fade-in (default = true)
  // options.prepend - If the element should prepend
  //   all other messages (default = false)
  function addMessageElement (el, options) {
    var $el = $(el);

    // Setup default options
    if (!options) {
      options = {};
    }
    if (typeof options.fade === 'undefined') {
      options.fade = true;
    }
    if (typeof options.prepend === 'undefined') {
      options.prepend = false;
    }

    // Apply options
    if (options.fade) {
      $el.hide().fadeIn(FADE_TIME);
    }
    if (options.prepend) {
      $messages.prepend($el);
    } else {
      $messages.append($el);
    }
    $messages[0].scrollTop = $messages[0].scrollHeight;
  }

  // Prevents input from having injected markup
  function cleanInput (input) {
    return $('<div/>').text(input).html() || input;
  }

  // Updates the typing event
  function updateTyping () {
    if (connected) {
      if (!typing) {
        typing = true;
        socket.emit('typing');
      }
      lastTypingTime = (new Date()).getTime();

      setTimeout(function () {
        var typingTimer = (new Date()).getTime();
        var timeDiff = typingTimer - lastTypingTime;
        if (timeDiff >= TYPING_TIMER_LENGTH && typing) {
          socket.emit('stop_typing');
          typing = false;
        }
      }, TYPING_TIMER_LENGTH);
    }
  }

  // Gets the 'X is typing' messages of a user
  function getTypingMessages (data) {
    return $('.typing.message').filter(function (i) {
      return $(this).data('username') === data.username;
    });
  }

  // Gets the color of a username through our hash function
  function getUsernameColor (username) {
    // Compute hash code
    var hash = 7;
    for (var i = 0; i < username.length; i++) {
       hash = username.charCodeAt(i) + (hash << 5) - hash;
    }
    // Calculate color
    var index = Math.abs(hash % COLORS.length);
    return COLORS[index];
  }


  // when user leave the page
  window.onbeforeunload = function (e) {
     socket.emit('del_user', {'username':username, 'user_id': user_id});

  };


  // Keyboard events

  $window.keydown(function (event) {
    // When the client hits ENTER on their keyboard
    if (event.which === 13) {
      if (username) {
        sendMessage();
        socket.emit('stop_typing');
        typing = false;
      } else {
        setUsername();
      }
    }
  });

  $inputMessage.on('input', function() {
    updateTyping();
  });

  // Socket events
  // Whenever the server emits 'new message', update the chat body
  socket.on('new_message', function (data) {
    if (data['user_id']==user_id) return;
    addChatMessage(data);
  });

  // Whenever the server emits 'user joined', log it in the chat body
  socket.on('user_joined', function (data) {
    if (data['user_id']==user_id) return;
    log(data.username + ' joined');
    addParticipantsMessage(data);
  });

  // Whenever the server emits 'user left', log it in the chat body
  socket.on('user_left', function (data) {
    if (data['user_id']==user_id) return;
    log(data.username + ' left');
    addParticipantsMessage(data);
    removeChatTyping(data);
  });

  // Whenever the server emits 'typing', show the typing message
  socket.on('typing', function (data) {
    if (data['user_id']==user_id) return;
    addChatTyping(data);
  });

  // Whenever the server emits 'stop typing', kill the typing message
  socket.on('stop_typing', function (data) {
    if (data['user_id']==user_id) return;
    removeChatTyping(data);
  });
});
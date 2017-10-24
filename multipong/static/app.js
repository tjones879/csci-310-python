var socket = io.connect(location.protocol + "//" + document.domain + ':' + location.port);
socket.on('connect', function() {
    //Do something on connect
});

function draw_ui(data) {
    var $container = $("#container");
    var $input_label = $('<label>', {id: "input_label", text: "Message: "});
    var $input_text = $('<input>', {id: "message_input", type: "text"});
    var $send_message = $('<input>', {id: "message_send", type: "button", value: "Send"});
    var $messages = $('<div>', {id: "messages"});
    $send_message.click(function () {
        socket.emit('message', {message: $input_text.val()});
    });
    $container.empty();
    $container.append($input_label);
    $container.append($input_text);
    $container.append($send_message);
    $container.append($messages);
}

socket.on('user.name.get', function() {
    $("#container").empty();
    var $username_input = $('<input>', {type: "text", id: "username_input"});
    var $submit_button = $('<input>', {type: "button", id: "submit_button", value: "Set Username"});
    $submit_button.click(function () {
        socket.emit("user.name.set", {username: $username_input.val()});
    });
    $("#container").append($username_input);
    $("#container").append($submit_button);
});

socket.on('message', function(data) {
    console.log(data);
    var $p = $('<p>');
    $p.append(data.username + ": " + data.message);
    $("#messages").append($p);
});

socket.on('user.ready', function(data) {
    console.log(data);
    socket.emit('user.room.join'); //join a random room
    draw_ui();
});


var socket = io.connect(location.protocol + "//" + document.domain + ':' + location.port);
socket.on('connect', function() {
    // emit a connect message
    socket.emit('client_connected', {data: 'New Client!'});
    $("#container").empty();
    var $test_button = $('<button>', {id: "test_button"});
    $test_button.innerText = "Test";
    $test_button.click(function () {socket.emit('test_event', "it works!")});
    var $messages = $('<div>', {id: "messages"});
    $("#container").append($test_button);
    $("#container").append($messages);
});

function test_message() {
    socket.emit('test_event', {data: "it works!"});
}

socket.on('test_response', function(data) {
   var $p = $('<p>');
   $p.append(data.data);
   $("#messages").append($p);
   console.log(data);
});
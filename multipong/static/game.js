var Game = {};
Game.init = function() {
    console.log("Game Init");
    var $container = $("#container");
    var $row1 = $("<div>", {id: "row1", class: "row"});
    var $row2 = $("<div>", {id: "row2", class: "row"});
    var $row3 = $("<div>", {id: "row3", class: "row"});
    var $debug = $('div', {id: "debug", class: "debug, col-md-4 pull-right"});
    var $messagebox = $('<div>', {id: "messages"});
    var $username_label = $('<label>', {id: "username_label", text: "Enter Your Name: "})
    var $username_input = $('<input>', {type: "text", id: "username_input"})
    var $submit_button = $('<input>', {type: "button", id: "submit_button", value: "Set Username"})
    $submit_button.click(function () {
        Client.requestNewPlayer($username_input.val());
    });
    $row1.append($debug);
    $row2.append($username_label, $username_input, $submit_button);
    $row3.append($messagebox);
    $container.empty();
    $container.append($row1, $row2, $row3);
};

Game.create = function() {
    Game.playerMap = {}; // Keep track of other players in room
    // Setup canvas and establish game loop
    // Test UI
    var $row2 = $("#row2");
    var $messageform = [
        $('<label>', {id: "input_label", text: "Message: "}),
        $('<input>', {id: "message_input", type: "text"}),
        $('<input>', {id: "message_send", type: "button", value: "Send"}),
        $('<input>', {id: "logout_button", type: "button", value: "Logout"})
    ];
    $messageform[2].click(function(){Client.socket.emit('usermessage', {message: $messageform[1].val()});});
    $messageform[3].click(function(){Client.socket.emit('logout');});
    $row2.empty();
    $row2.append($messageform);
    // end Test UI

};


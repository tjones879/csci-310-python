var Client = {};
Client.socket = io.connect();

// outgoing events
Client.requestNewPlayer = function(username) {
    Client.socket.emit('newplayer', {"username": username});
};

Client.logout = function() {
    Client.socket.emit('logout');
};

// incoming event handlers
Client.playerReady = function(data) {
    Game.create();
};
Client.roomJoin = function(data) {
    var $p = $('<p>');
    $p.append(data.username + " has joined the room.");
    $("#messages").append($p);
};
Client.roomUpdate = function(data) {
    console.log(data);
};
Client.onMessage = function(data) {
    var $p = $('<p>');
    $p.append(data.username + ": " + data.message);
    $("#messages").append($p);
};
Client.tick = function() {
    Client.socket.emit('roomupdate', {}); // FUTURE: Send player data
};

Client.askUsername = function() {
    Game.init()
};

// Event registration
Client.socket.on('connect', function() {
    console.log("connected");
    Game.init();
});
Client.socket.on('usermessage', Client.onMessage);
Client.socket.on('tick', Client.tick);
Client.socket.on('roomupdate', Client.roomUpdate);
Client.socket.on('askusername', Client.askUsername);
Client.socket.on('playerready', Client.playerReady);
Client.socket.on('roomjoin', Client.roomJoin);

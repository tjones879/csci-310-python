/* global io */
var Client = new function(){
    var socket = io.connect();
    
    this.init = function(){
        //<Event Registration
        socket.on('gamedata', onGameData);
        socket.on('toggledebug', onToggleDebug);
        socket.on('debug', onDebug);
        socket.on('serverUpdate', onServerUpdate);

        socket.on('connect', function() {
            console.log("connected");
            //start the background game loop
        });
    }

    //<Event Handlers>
    function onGameData(data) {
        app.onGameData(data);
    }

    function onDebug(data) {
        console.log(data);
    }

    function onToggleDebug(data) {
        if (data.debug) {
            app.toggleDebugMode();
        }
    }
    function onServerUpdate(data){
        
    }
    this.logInUser = function(username) {
        socket.emit('login', {"username": username});
    };

    this.logOutUser = function() {
        socket.emit('logout');
    };
    
    this.clientUpdate = function(){
        socket.emit('clientUpdate');
    }
    
    this.ballHit = function(){
        socket.emit('ballHit');
    }
    //</Event Handlers>

    //OLD STUFF
    // outgoing events
    /*
    
    this.toggleDebug = function(){
        this.socket.emit('toggleDebug');
    }
    
    // incoming event handlers
    this.playerReady = function(data) {
        Game.create();
    };
    this.roomJoin = function(data) {
        var $p = $('<p>');
        $p.append(data.username + " has joined the room.");
        $("#messages").append($p);
    };
    this.roomUpdate = function(data) {
        console.log(data);
    };
    this.onMessage = function(data) {
        var $p = $('<p>');
        $p.append(data.username + ": " + data.message);
        $("#messages").append($p);
    };
    this.tick = function() {
        socket.emit('roomupdate', {}); // FUTURE: Send player data
    };
    
    this.askUsername = function() {
        Game.init()
    };
    */
    
    

}
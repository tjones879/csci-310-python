/* global io */
var Client = new function(){
    var socket = io.connect();

    this.init = function(){
        //<Event Registration
        socket.on('toggledebug', onToggleDebug);
        socket.on('debug', onDebug);
        socket.on('serverUpdate', onServerUpdate);
        socket.on('latencyHandshake', onLatencyReply);

        socket.on('connect', function() {
            console.log("connected");
            latencyHandshake();
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
        if(data.action == 'init')
          app.initUpdate(data);
        else if(data.action == 'cycleUpdate')
          app.cycleUpdate(data);
        else if(data.action == 'forceUpdate')
          app.forceUpdate(data);
    }
    function latencyHandshake() {
        var time = Date.now() / 1000
        var j = '{"clientTime" : ' + time + '}';
        socket.emit('latencyCheck', j);
    }
    function onLatencyReply(resp) {
        app.calcDriftTime(resp.data.clientTime, resp.serverTime);
    }
    this.logInUser = function(username) {
        socket.emit('login', {"username": username});
    };

    this.logOutUser = function() {
        socket.emit('logout');
    };

    this.sendClientUpdate = function(){
        var j = '{"balls" : ' + JSON.stringify(app.getBalls()) + '}';
        socket.emit('clientUpdate', j);
    }

    this.ballHit = function(){
        socket.emit('ballHit');
    }
}

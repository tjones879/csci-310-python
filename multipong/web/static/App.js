//App class to control the flow of the game and overall game components
function App(){
  //initialize public variables
  var pongBalls = new Array();
  var debug = false;
  var LOOP = null;
  var paddleAudio = new Audio('static/audio/paddle-hit.wav');
  var wallAudio = new Audio('static/audio/wall-hit.wav');
  var driftTime = 0.0; // server's time - local time
  var previousTime = new Date().getTime();
  var frameTime = new Date().getTime();
  var updateTime = new Date().getTime();
  this.elapsedTime = 0;
  var frames = 0;
  var logedIn = false;

	//tables
	var bounceTable = [[-1, 1], [1, -1], [1, 1], [-1, -1]];

  //Initial state of the game... not logged in
  this.init = function(){
    //initialize game state
    ui.init(this);
    Client.init();
  }

  //The game loop
  var loop = function(){
    getElapsedTime();
		ui.updateInput(this.elapsedTime);
    for(var a = 0; a < pongBalls.length; a++){
      pongBalls[a].pos.x += pongBalls[a].vec.x * this.elapsedTime;
      pongBalls[a].pos.y += pongBalls[a].vec.y * this.elapsedTime;
			
			//are we in range of left walls
			if(pongBalls[a].pos.x <= 292){
				//did we hit upper left wall
				if(pongBalls[a].pos.y + pongBalls[a].pos.x <= 292)
					edgeHit(a, 3);
				//did we hit lower left wall
				else if(pongBalls[a].pos.y - pongBalls[a].pos.x >= 706)
					edgeHit(a, 2);
				//did we hit middle left wall
				else if(pongBalls[a].pos.x <= 0)
					edgeHit(a, 0);
			}
			//are we in range of right walls
			else if(pongBalls[a].pos.x >= 706){
				//did we hit upper right wall
				if(pongBalls[a].pos.x - pongBalls[a].pos.y >= 706)
					edgeHit(a, 2);
				//did we hit lower right wall
				else if(pongBalls[a].pos.y + pongBalls[a].pos.x >= 1706)
					edgeHit(a, 3);
				//did we hit middle right wall
				else if(pongBalls[a].pos.x >= 999)
					edgeHit(a, 0);
			}
			else{
				//did we hit top wall
				if(pongBalls[a].pos.y <= 0)
					edgeHit(a, 1);
				//did we hit bottom wall
				else if(pongBalls[a].pos.y >= 999)
					edgeHit(a, 1);
			}
    }
    evalFps();
    if(logedIn)
      evalClientUpdate();
    ui.updateCanvas(pongBalls);
    LOOP = setTimeout(loop, 10);
  }

	var edgeHit = function(theBall, theEdge){
    pongBalls[theBall].pos.x -= pongBalls[theBall].vec.x * this.elapsedTime;
    pongBalls[theBall].pos.y -= pongBalls[theBall].vec.y * this.elapsedTime;
		
		//Is the edge a horizontal or vertical one
		if(theEdge < 2){
			pongBalls[theBall].vec.x *= bounceTable[theEdge][0];
			pongBalls[theBall].vec.y *= bounceTable[theEdge][1];
		}
		//Is the edge a diagonal
		else{
			var vecx = pongBalls[theBall].vec.x;
			var vecy = pongBalls[theBall].vec.y;
			pongBalls[theBall].vec.x = vecy * bounceTable[theEdge][0];
			pongBalls[theBall].vec.y = vecx * bounceTable[theEdge][1];
		}
	
		wallAudio.play();
	}

  //calculte the elapsed time for use in frame independent logic
  var getElapsedTime = function(){
    var currentTime = new Date().getTime();
    this.elapsedTime = currentTime - previousTime;
    this.elapsedTime /= 1000;
    previousTime = currentTime;
  }

  //check and reset fps vars, display fps value in debug window
  var evalFps = function(){
    var currentTime = new Date().getTime();
    if(currentTime - frameTime >= 1000){
      frameTime = currentTime;
      //console.log('fps', frames);
      frames = 0;
    }
    frames++;
  }

  //check to see if it is time to send a client update to server
  //if it is then send it.
  var evalClientUpdate = function(){
    var currentTime = new Date().getTime();
    if(currentTime - updateTime >= 1000){
      updateTime = currentTime;
      Client.sendClientUpdate();
      //console.log('client update');
    }
  }


  //Happens on login form submission
  this.logInUser = function(){
    ui.logInUser();
    Client.logInUser(ui.user);
    logedIn = true;
  }

  //Happens on close button click
  this.logOutUser = function(){
    ui.logOutUser();
    Client.logOutUser();
    logedIn = false;
  }

  //Toggles Popup showing framerate keycodes and other usefull info
  this.toggleDebugMode = function(){
    debug = !debug;
  }

  var haveBall = function(id){
    for(var a = 0; a < pongBalls.length; a++){
      if(pongBalls[a].id == id)
        return true;
    }
    return false;
  }

  //function fired on forced serverUpdate action=forceUpdate
  //tells client to reinitialize game data including players, leaderboard and balls
  this.forceUpdate = function(data){
    //Clear current client game state then update
    pongBalls = new Array();
    this.cycleUpdate(data);
  }

  //function fired on normal serverUpdate action=cycleUpdate
  //just to update ball and player paddle positions
  this.cycleUpdate = function(data){
    var latency = (Date.now() / 1000) - data.timestamp - this.driftTime;
    //update the balls
    for(var a = 0; a < data.balls.length; a++){
      if(!haveBall(data.balls[a].id)){
        ball = new Ball();
        ball.init(data.balls[a].id, data.balls[a].pos.x, data.balls[a].pos.y, data.balls[a].vec.x, data.balls[a].vec.y, data.balls[a].type);
        pongBalls.push(ball);
      }
      else{
        ball = getBall(data.balls[a].id);
        ball.vec.x = data.balls[a].vec.x;
        ball.vec.y = data.balls[a].vec.y;
        ball.pos.x = data.balls[a].pos.x + ball.vec.x * latency;
        ball.pos.y = data.balls[a].pos.y + ball.vec.y * latency;
      }
    }

    //update player paddle positions
  }

  //function fired on socket serverUpdate action=initUpdate
  //To set up spectator on page load
  this.initUpdate = function(data){
    ui.setRoom(data.id);
    this.cycleUpdate(data);
    loop();
  }

  this.calcDriftTime = function(clientTime, serverTime) {
    var ping = ((Date.now() / 1000) - clientTime) / 2;
    this.driftTime = serverTime - clientTime - ping;
  }

  var getBall = function(id){
    for(var a = 0; a < pongBalls.length; a++){
      if(pongBalls[a].id == id)
        return pongBalls[a];
    }
    return false
  }

  //returns the pongballs for use in JSON packaging in socket io
  this.getBalls = function(){
    return pongBalls;
  }
}

var app = new App();
var ui = new Ui();
var player = new Paddle();
app.init();

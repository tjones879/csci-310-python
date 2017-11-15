//App class to control the flow of the game and overall game components
/*global ui*/
/*global Client*/
function App(){
  //initialize public variables
  var pongBalls = new Array();
  var debug = false;
  var LOOP = null;
  var paddleAudio = new Audio('static/audio/paddle-hit.wav');
  var wallAudio = new Audio('static/audio/wall-hit.wav');
  var previousTime = new Date().getTime();
  var frameTime = new Date().getTime();
  this.elapsedTime = 0;
  var frames = 0;

  //Initial state of the game... not logged in
  this.init = function(){
    //initialize game state
    ui.init(this);
    Client.init();
  }

  //The game loop
  var loop = function(){
    getElapsedTime();
    for(var a = 0; a < pongBalls.length; a++){
      pongBalls[a].pos.x += pongBalls[a].vec.x * this.elapsedTime;
      pongBalls[a].pos.y += pongBalls[a].vec.y * this.elapsedTime;
      if(pongBalls[a].pos.x >= ui.arenaSize || pongBalls[a].pos.x < 0){
        if(player.hitBall(pongBalls[a].pos.x, pongBalls[a].pos.y)){
          paddleAudio.play();
          console.log('hit');
        }
        else
          wallAudio.play();
        pongBalls[a].vec.x *= -1;
      }
      if(pongBalls[a].pos.y >= ui.arenaSize || pongBalls[a].pos.y < 0){
        if(player.hitBall(pongBalls[a].pos.x, pongBalls[a].pos.y)){
          paddleAudio.play();
          console.log('hit');
        }
        else
          wallAudio.play();
        pongBalls[a].vec.y *= -1;
      }
    }
    ui.updateCanvas(pongBalls);
    setTimeout(loop, 20);
  }

  var getElapsedTime = function(){
    var currentTime = new Date().getTime();
    this.elapsedTime = currentTime - previousTime;
    this.elapsedTime /= 1000;
    previousTime = currentTime;
    if(currentTime - frameTime >= 1000){
      frameTime = currentTime;
      console.log('fps', frames);
      frames = 0;
    }
    frames++;
  }

  //Happens on login form submission
  this.logInUser = function(){
    ui.logInUser();
    Client.logInUser(ui.user);
  }

  //Happens on close button click
  this.logOutUser = function(){
    ui.logOutUser();
    Client.logOutUser();
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

  this.forceUpdate = function(data){
    //Clear current client game state then update
    pongBalls = new Array();
    this.cycleUpdate(data);
  }

  this.cycleUpdate = function(data){
    //update the balls
    for(var a = 0; a < data.balls.length; a++){
      if(!haveBall(data.balls[a].id)){
        ball = new Ball();
        ball.init(data.balls[a].id, data.balls[a].pos.x, data.balls[a].pos.y, data.balls[a].vec.x, data.balls[a].vec.y, data.balls[a].type);
        pongBalls.push(ball);
      }
      else{
        ball = getBall(data.balls[a].id);
        ball.pos.x = data.balls[a].pos.x;
        ball.pos.y = data.balls[a].pos.y;
        ball.vec.x = data.balls[a].vec.x;
        ball.vec.y = data.balls[a].vec.y;
      }
    }

    //update player paddle positions
  }

  this.initUpdate = function(data){
    ui.setRoom(data.id);
    this.cycleUpdate(data);
    setTimeout(loop, 10);
  }
}

//User Interface Class to controll the user interface elements
function Ui(){
  //initialize private ui variables
  var loginForm = document.getElementById("login-cmp");
  var loginName = document.getElementById("nickname-input");
  var loginBtn = document.getElementById("nickname-button");
  var closeBtn = document.getElementById("close-cmp");
  var username = document.getElementById("username");
  var canvas = document.getElementById("canvas");
  var leaderboard = document.getElementById("leaderboard");
  var leaderboardBtn = document.getElementById("leaderboard-btn");
  var roomId = document.getElementById("room-id");

  var screenWidth = window.innerWidth;
  var screenHeight = window.innerHeight;
  var screenScale = 1;
  var context = canvas.getContext("2d");
  var keytime = new Date();

  this.user = "Not Logged In";
  this.arenaSize = 1000;


  //set up ui event listeners
  this.init = function(app){
    loginBtn.onclick = app.logInUser;
    closeBtn.onclick = app.logOutUser;
    leaderboardBtn.onclick = toggleLeaderboard;
    resize();
    window.onresize = resize;
    username.innerHTML = this.user;
    window.onkeydown = processAppInput;
  }

  //Renders components on canvas
  this.updateCanvas = function(pongBalls){
    context.clearRect(0, 0, screenWidth, screenHeight);
    //Drawing all balls
    for(var a = 0; a < pongBalls.length; a++){
      context.fillRect(parseInt(pongBalls[a].pos.x) * screenScale, parseInt(pongBalls[a].pos.y) * screenScale, 10, 10);
    }
    //Drawing the paddle
    player.draw(context);
  }

  //In the event the user resizes browser
  var resize = function(){
    screenWidth = window.innerWidth - 4;
    screenHeight = window.innerHeight - 4;
    if(screenWidth < screenHeight){
      if(screenWidth < ui.arenaSize){
        screenScale = screenWidth / ui.arenaSize;
      }
    }
    else{
      if(screenHeight < ui.arenaSize){
        screenScale = screenHeight / ui.arenaSize;
      }
    }
    canvas.setAttribute("width", parseInt(ui.arenaSize * screenScale));
    canvas.setAttribute("height", parseInt(ui.arenaSize * screenScale));
  }

  this.getScreenHeight = function(){
    return screenHeight;
  }

  this.getScreenScale = function(){
    return screenScale;
  }

  //Toggles a few ui components and updates info
  this.logOutUser = function(){
    loginForm.classList.toggle("visible");
    this.user = "Not Logged In";
    username.innerHTML = this.user;
    closeBtn.classList.toggle('visible');
  }

  //Toggles a few ui components and updates info
  this.logInUser = function(){
    loginForm.classList.toggle("visible");
    this.user = loginName.value;
    username.innerHTML = this.user;
    closeBtn.classList.toggle('visible');
  }

  var processAppInput = function(event){
    if(new Date() - keytime > 10){
      keytime = new Date();
      //console.log(keytime);
      //input if user is logged in
      if(!loginForm.classList.contains("visible")){
        console.log(event.keyCode);
        if(event.keyCode == 113)//q
          app.logOutUser();
        else if(event.keyCode == 63)//?
          app.toggleDebugMode();
        else if(event.keyCode == 65)//a
          player.moveLeft();
        else if(event.keyCode == 68)//d
          player.moveRight();
      }
      //input if user is not logged in
      else{
        if(event.keyCode == 13)//ENTER
          app.logInUser();
      }
    }
  }

  this.setRoom = function(id){
    roomId.innerHTML = '(' + id + ')';
  }

  var toggleLeaderboard = function(){
    leaderboard.classList.toggle('visible');
  }
}

function Ball(){
  this.ui = 0;
  this.pos = {x:0, y:0};
  this.vec = {x:0, y:0};
  
  this.init = function(auid, ax, ay, axDir, ayDir){
    this.id = auid;
    this.pos.x = ax;
    this.pos.y = ay;
    this.vec.x = axDir;
    this.vec.y = ayDir;
  }
}

function Paddle(){
  var pos = 500;
  var width = 100;

  this.moveLeft = function(){
    pos -= 10;
  }

  this.moveRight = function(){
    pos += 10;
  }

  this.hitBall = function(x, y){
    return y >= ui.arenaSize && x >= pos - width / 2 && x <= pos + width / 2;
  }

  this.draw = function(context){
    var x = (pos - width / 2) * ui.getScreenScale();
    var y = (ui.getScreenHeight() - 10);
    context.fillRect(x, y, width * ui.getScreenScale(), 10);
  }
}

var player = new Paddle();
var app = new App();
var ui = new Ui();

app.init();

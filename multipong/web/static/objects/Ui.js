//User Interface Class to controll the user interface elements
ui = new function(){
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
		
		//Draw Table
		var firstBoundry = 0 * screenScale;
		var secondBoundry = 999 * screenScale;
		this.firstPoint = 292 * screenScale;
		this.secondPoint = 706 * screenScale;
		context.beginPath();
		context.moveTo(this.firstPoint, firstBoundry);
		context.lineTo(this.secondPoint, firstBoundry);
		context.lineTo(secondBoundry, this.firstPoint);
		context.lineTo(secondBoundry, this.secondPoint);
		context.lineTo(this.secondPoint, secondBoundry);
		context.lineTo(this.firstPoint, secondBoundry);
		context.lineTo(firstBoundry, this.secondPoint);
		context.lineTo(firstBoundry, this.firstPoint);
		context.lineTo(this.firstPoint, firstBoundry);
		context.stroke();

    //Draw Balls
		for(var a = 0; a < pongBalls.length; a++){
      context.fillRect(parseInt(pongBalls[a].pos.x) * screenScale, parseInt(pongBalls[a].pos.y) * screenScale, 10, 10);
    }
    //Drawing the paddle
    player.draw(context);
  }

  //In the event the user resizes browser
  var resize = function(){
    screenWidth = window.innerWidth - 20;
    screenHeight = window.innerHeight - 110;
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

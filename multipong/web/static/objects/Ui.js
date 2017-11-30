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
	var padding = 10;
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
		var firstBoundry = padding * screenScale;
		var secondBoundry = (999 + padding) * screenScale;
		var firstPoint = (292 + padding) * screenScale;
		var secondPoint = (706 + padding) * screenScale;
		context.beginPath();
		context.moveTo(firstPoint, firstBoundry);
		context.lineTo(secondPoint, firstBoundry);
		context.lineTo(secondBoundry, firstPoint);
		context.lineTo(secondBoundry, secondPoint);
		context.lineTo(secondPoint, secondBoundry);
		context.lineTo(firstPoint, secondBoundry);
		context.lineTo(firstBoundry, secondPoint);
		context.lineTo(firstBoundry, firstPoint);
		context.lineTo(firstPoint, firstBoundry);
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
        screenScale = screenHeight / (ui.arenaSize + 2 * padding);
      }
    }
    canvas.setAttribute("width", parseInt((ui.arenaSize + 2 * padding) * screenScale));
    canvas.setAttribute("height", parseInt((ui.arenaSize + 2 * padding) * screenScale));
  }

  this.getScreenHeight = function(){
    return screenHeight;
  }

  this.getScreenScale = function(){
    return screenScale;
  }

	this.getPadding = function(){
		return padding;
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

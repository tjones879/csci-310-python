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
	var padding = 10;
  var context = canvas.getContext("2d");
	var keys = new Array(256);

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
    window.onkeydown = keyDownInput;
		window.onkeyup = keyUpInput;
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

	this.updateInput = function(elapsedTime){
		if(keys[65] || keys[87]){
			player.decrement(elapsedTime);
		}
		if(keys[68] || keys[83]){
			player.increment(elapsedTime);
		}
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

  var keyDownInput = function(event){
		if(!loginForm.classList.contains('visible')){
			keys[event.keyCode] = true;
		}
		else
			if(event.keyCode == 13)//ENTER
				app.logInUser();
	}

	var keyUpInput = function(event){
		if(!loginForm.classList.contains('visible'))
			keys[event.keyCode] = false;
	}

  this.setRoom = function(id){
    roomId.innerHTML = '(' + id + ')';
  }

  var toggleLeaderboard = function(){
    leaderboard.classList.toggle('visible');
  }
}

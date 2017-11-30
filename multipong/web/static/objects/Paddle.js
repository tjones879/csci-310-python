function Paddle(){
  var pos = .5;
  var width = 100;
	var wall = 6;

  this.moveLeft = function(){
    pos -= .05;
		if(pos < 0)
			pos = 0;
  }

  this.moveRight = function(){
    pos += .05;
		if(pos > 1)
			pos = 1;
  }

  this.hitBall = function(x, y){
    return y >= ui.arenaSize && x >= pos - width / 2 && x <= pos + width / 2;
  }

  this.draw = function(context){
		var offset = 292 + ui.getPadding();
		var wallLength = 414;
   	var x;
		var y;

		if(wall == 0){
			x = (pos * wallLength + offset - width / 2) * ui.getScreenScale();
 		  y = ui.getScreenHeight() - (10 * ui.getScreenScale());
    	context.fillRect(x, y, width * ui.getScreenScale(), 10 * ui.getScreenScale());
		}
		else if(wall == 2){
 		  x = 0;
			y = (pos * wallLength + offset - width / 2) * ui.getScreenScale();
    	context.fillRect(x, y, 10 * ui.getScreenScale(), width * ui.getScreenScale());
		}
		else if(wall == 4){
			x = (pos * wallLength + offset - width / 2) * ui.getScreenScale();
 		  y = 0;
    	context.fillRect(x, y, width * ui.getScreenScale(), 10 * ui.getScreenScale());
		}
		else if(wall == 6){
 		  x = ui.getScreenHeight() - (10 * ui.getScreenScale());
			y = (pos * wallLength + offset - width / 2) * ui.getScreenScale();
    	context.fillRect(x, y, 10 * ui.getScreenScale(), width * ui.getScreenScale());
		}

  }
}

var player = new Paddle();

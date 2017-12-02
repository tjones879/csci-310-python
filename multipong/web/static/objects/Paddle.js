function Paddle(){
  this.pos = .5;
  var width = 100;
	var wall = 6;

  this.decrement = function(elapsedTime){
    this.pos -= elapsedTime * 1.5;
		if(this.pos < 0)
			this.pos = 0;
  }.bind(this);

  this.increment = function(elapsedTime){
    this.pos += elapsedTime * 1.5;
		if(this.pos > 1)
			this.pos = 1;
  }.bind(this);

  this.hitBall = function(x, y){
    return y >= ui.arenaSize && x >= this.pos - width / 2 && x <= this.pos + width / 2;
  }

  this.draw = function(context){
		var offset = 292 + ui.getPadding();
		var wallLength = 414;
   	var x;
		var y;

		if(wall == 0){
			x = (this.pos * wallLength + offset - width / 2) * ui.getScreenScale();
 		  y = ui.getScreenHeight() - (10 * ui.getScreenScale());
    	context.fillRect(x, y, width * ui.getScreenScale(), 10 * ui.getScreenScale());
		}
		else if(wall == 2){
 		  x = 0;
			y = (this.pos * wallLength + offset - width / 2) * ui.getScreenScale();
    	context.fillRect(x, y, 10 * ui.getScreenScale(), width * ui.getScreenScale());
		}
		else if(wall == 4){
			x = (this.pos * wallLength + offset - width / 2) * ui.getScreenScale();
 		  y = 0;
    	context.fillRect(x, y, width * ui.getScreenScale(), 10 * ui.getScreenScale());
		}
		else if(wall == 6){
 		  x = ui.getScreenHeight() - (10 * ui.getScreenScale());
			y = (this.pos * wallLength + offset - width / 2) * ui.getScreenScale();
    	context.fillRect(x, y, 10 * ui.getScreenScale(), width * ui.getScreenScale());
		}

  }
}

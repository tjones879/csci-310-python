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

//Class for all pong balls to hold data and perform update/ui related functions
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


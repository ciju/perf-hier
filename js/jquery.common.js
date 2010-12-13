jQuery.fn.setupExtras = function(setup, options) {
  for(extra in setup) {
    var self = this;
    if(setup[extra] instanceof Array) {
      for(var i=0; i<setup[extra].length; i++)
        setup[extra][i].call(self, options);
    } else if (setup[extra] instanceof Function){
      console.log('se: fn');
      setup[extra].call(self, options);
    } else {
      console.log('se: ?');
    }
  }
};

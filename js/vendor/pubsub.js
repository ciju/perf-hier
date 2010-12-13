/**
 * jQuery pub/sub plugin by Peter Higgins (dante@dojotoolkit.org)
 * 
 * Loosely based on Dojo publish/subscribe API, limited in scope. Rewritten blindly.
 * 
 * Original is (c) Dojo Foundation 2004-2009. Released under either AFL or new BSD, 
 * 
 * formatting by ciju
 * 
 * @see http://dojofoundation.org/license for more information.
 * 
 */
;(function(d, dbg){
  var cache = {};

  /**
   * @desc Publish some data on a named topic.
   * 
   * @param topic String : the channel to publish on 
   * @param args Array : the data to publish. Each array item is
   *                     converted into an ordered arguments on the 
   *                     subscribed functions.
   * @example Publish stuff on '/some/topic'. Anything subscribed 
   *          will be called with a function signature like: 
   *           function(a,b,c){ ... }
   *           $.publish("/some/topic", ["a","b","c"]);
   * 
   */
    d.publish = function(topic){
        if (!cache[topic])  return;
        dbg.info('publishing ', topic);
        for (var i=0, len=cache[topic].length; i<len; i++) {
            cache[topic][i].apply(this, Array.prototype.slice.apply(arguments, [1]) || []);
        }
    };

  /**
   * @desc Register a callback on a named topic.
   * 
   * @param topic String : The channel to subscribe to
   * @param callback Function : The handler event. Anytime something is 
   *                            $.publish'ed on a subscribed channel, the 
   *                            callback will be called with the published
   *                            array as ordered arguments.
   * 
   * @returns Array : A handle which can be used to unsubscribe this particular 
   *                  subcription.
   * 
   * @example 
   *          $.subscribe("/some/topic", function(a, b, c){ handle data });
   */
  d.subscribe = function(topic, callback){
    if(!cache[topic]){
      cache[topic] = [];
    }
    cache[topic].push(callback);
    return [topic, callback]; // Array
  };

  /**
   * @desc Register callback on an array of topics. Any one of 
   * them could invoke the callback.
   * 
   * @param topics Array: Array of strings of topics.
   * @param callabck Function: The event handler.
   * 
   */
  d.subscribe_all = function (topics, cb) {
    var topic;
    for (var i=0; i<topics.length; i++) {
      topic = topics[i];
      if (!cache[topic]) {
        cache[topic]= [];
      }
      cache[topic].push(cb);
    }
    return [topic, cb];
  };

  /**
   * @desc Disconnect a subscribed function for a topic.
   * 
   * @param handle Array: The return value from a $.subscribe call.
   * 
   * @example 
   *          var handle = $.subscribe("/something", function(){}); 
   *          $.unsubscribe(handle);
   */
  d.unsubscribe = function(handle, topic){
    var t = topic || handle[0];
    d.each(cache[t], function(idx){
      if(this == handle[1]){
	cache[t].splice(idx, 1);
      }
    });
  };

})(jQuery, debug);
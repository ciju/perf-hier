var PerfHier = {dev:true};

// (function ($, app) {
//   [].indexOf || (Array.prototype.indexOf = function(v, n){
//     n = (n == null) ? 0 : n; var m = this.length;
//     for(var i = n; i < m; i++) {
//       if(this[i] == v) return i;
//     }
    
//     return -1;
//   });
  
//   [].filter || (Array.prototype.filter = function(fun /*, thisp*/) {
//     var len = this.length >>> 0, res = [], thisp = arguments[1];
    
//     for (var i = 0; i < len; i++) {
//       if (i in this) {
//         var val = this[i];
//         if (fun.call(thisp, val, i, this)) res.push(val);
//       }
//     }
    
//     return res;
//   });
  
//   if (!Array.forEach) {
    
//     Array.prototype.forEach = function (D, E) {
      
//       var C = E || window;
//       for (var B = 0, A = this.length; B < A; ++B) {
        
//         D.call(C, this[B], B, this);
//       }
//     };
//     Array.prototype.map = function (E, F) {
      
//       var D = F || window;
//       var A = [];
//       for (var C = 0, B = this.length; C < B; ++C) {
        
//         A.push(E.call(D, this[C], C, this));
//       }
//       return A
//     };
//     Array.prototype.filter = function (E, F) {
      
//       var D = F || window;
//       var A = [];
//       for (var C = 0, B = this.length; C < B; ++C) {
        
//         if (!E.call(D, this[C], C, this)) {
          
//           continue;
//         }
//         A.push(this[C]);
//       }
//       return A;
//     };
//     Array.prototype.every = function (D, E) {
      
//       var C = E || window;
//       for (var B = 0, A = this.length; B < A; ++B) {
        
//         if (!D.call(C, this[B], B, this)) {
          
//           return false;
//         }
//       }
//       return true;
//     };
//     Array.prototype.indexOf = function (B, C) {
      
//       var C = C || 0;
//       for (var A = 0; A < this.length; ++A) {
        
//         if (this[A] === B) {
          
//           return A;
//         }
//       }
//       return -1;
//     };
//   }
//   Array.prototype.contains = function (A) {
    
//     if (Array.contains) {
      
//       return this.contains(A);
//     }
//     return this.indexOf(A) > -1;
//   };
//   Array.prototype.insert = function (A) {
    
//     if (!this.contains(A)) {
      
//       this.push(A);
//     }
//   };
  
// });

// (function ($, app){

(function ($, dbg, app) {
  // backend calling functions.

    // ajax call to server for backend rpc functions.
    var req = $.fn.ph_request = function (fn_name, type, opts, cb, failure_cb) {
        if ((typeof(opts) === 'undefined') || $.isFunction(opts)) { //opts skipped ?
            cb = opts;
            failure_cb = cb;
            opts = {};
        }
        if (typeof(cb) === 'undefined') { //cb skipped ?
            cb = dbg.log;
        }
        var len = opts.length;

        opts.action = fn_name;
        $.ajax({
            type: type,
            url: '/rpc',
            data: opts,
            success: function (resp, textStatus) {
                if (!resp.status || resp.status != 'ok' || textStatus != 'success') {
                    failure_cb(resp);
                    return;
                }
                cb(resp.result);
            },
            error: function (req, textStatus, err) {
                dbg.warn('req error', textStatus, err);
                // todo: this is shitty man. how do we get the error messages.
                failure_cb(textStatus, err);
            },
            dataType: 'json'
        });
    };

    req('get_list_rpc_methods', 'GET', {},function (resp) {
        var posts = resp.methods.posts,
            gets = resp.methods.gets,
            PH_api = {},
            fn,
            i;
        for (i=0; i<gets.length; i++) {
            fn = gets[i].fun;
            PH_api[fn] = (function(fn) {
                return function () {
                    return req( fn, 'GET', arguments[0], arguments[1], arguments[2] );
                };
            }(fn));
        }
        
        for (i=0; i<posts.length; i++) {
            fn = posts[i].fun;
            PH_api[fn] = (function(fn) {
              return function () {
                  return req( fn, 'POST', arguments[0], arguments[1], arguments[2] );
              };
            }(fn));
        }
        
        $.publish( '/ph/api/available', app.api = PH_api );
    }, function (resp) {
        dbg.log( 'get_list_rpc_methods failed', resp );
    });

}(jQuery, debug, _ph));




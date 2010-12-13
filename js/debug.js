(function (dbg) {
    if (!window.debug || !printStackTrace) {
        return;
    }

    var log_methods = [ 'error', 'warn', 'info', 'debug', 'log' ]
    , owarn, olog, oinfo, odebug
    , i
    ;

    owarn = dbg.warn;
    dbg.warn = function () {
        var s = printStackTrace()
        , args = Array.prototype.slice.call(arguments)
        , path
        , f
        ;
        
        s.shift(); s.shift(); s.shift();
        // console.log(s[0], arguments, args);
        path = s[0].split('/');
        f = path[path.length-1];
        args.unshift(f+' -- ');
        owarn.apply(window, args);
    };

    olog = dbg.log;
    dbg.log = function () {
        var s = printStackTrace()
        , args = Array.prototype.slice.call(arguments)
        , path
        , f
        ;
        s.shift(); s.shift(); s.shift();
        // console.log(s[0], arguments, args);
        path = s[0].split('/');
        f = path[path.length-1];
        args.unshift(f+' -- ');
        olog.apply(window, args);
    };

    oinfo = dbg.info;
    dbg.info = function () {
        var s = printStackTrace()
        , args = Array.prototype.slice.call(arguments)
        , path
        , f
        ;
        s.shift(); s.shift(); s.shift();
        // console.log(s[0], arguments, args);
        path = s[0].split('/');
        f = path[path.length-1];
        args.unshift(f+' -- ');
        oinfo.apply(window, args);
    };

    odebug = dbg.debug;
    dbg.debug = function () {
        var s = printStackTrace()
        , args = Array.prototype.slice.call(arguments)
        , path
        , f
        ;
        s.shift(); s.shift(); s.shift();
        // console.log(s[0], arguments, args);
        path = s[0].split('/');
        f = path[path.length-1];
        args.unshift(f+' -- ');
        odebug.apply(window, args);
    };

})(debug);

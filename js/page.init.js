// stuffs to be included in the client pages.
(function () {

    // perf-hier top code
    (function (w, d, eattach, edetach, epre) {
        var app = w._phc = w._phc || {ts:{}};
        app.ts.page_start = +new Date;
        app.auto_tags = true;

        (function () {
            var intrvl, ready = false;

            function fn() {
                clearInterval(intrvl); intrvl = 0;
                if (!ready) { ready = true; edetach('load', fn, false); }
                if (typeof app.ts.dom_load_ts == 'undefined') {
                    app.ts.dom_load_ts = +new Date;
                    if (typeof app.send_events != 'undefined') app.send_events();
                }
            }

            eattach('load', fn, false);
            if (addEventListener)
                d.addEventListener('DOMContentLoaded', fn, false);
            else if (w.attachEvent && self == self.top)
                intrvl = setInterval(function () {
                    try { if (d.body) { d.documentElement.doScroll('left'); fn(); } } catch (x) {}
                }, 30);
        })();

    })(window,
       document,
       window.attachEvent || window.addEventListener,
       window.detachEvent || window.removeEventListener,
       window.attachEvent ? 'on' :'');


    
    // perf-hier custom code helper
    (function (app) {
        var cmds = ["start", "end"], cmd, i, len;
        app.raw_tags = app.raw_tags || []; app.auto_tags = false;
        for (i=0, len=cmds.length; i<len; i++) {
            cmd = cmds[i];
            app[cmd] = (function (cmd) {
                return (function (str, time) {
                    time = time || +new Date;
                    app.raw_tags.push([cmd, str, time]);
                });
            }(cmd));
        }
        app.start("page");
    })(window._phc = {});
    

    // perf-hier bottom code
    (function(app) { try {
        if (!app.auto_tags) { app.end(); } else { app.ts.body_end = +new Date;}
        app.ph_id = REPLACE_WITH_PHC_PROJECT_ID;
        var ph = document.createElement('script'); ph.type = 'text/javascript'; ph.async = true;
        ph.src = "//perf-hier.appspot.com/build/client.js";
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ph, s);
    } catch (x) {} })(_phc);
    
});


// (function (w, d, eattach, edetach, epre) {
//     // top
//     var app = w._phc = w._phc || {};
//     var cmds = ["start", "end", "event"], cmd, i, len;
    
//     app.raw_tags = app.raw_tags || [];
//     for (i=0, len=cmds.length; i<len; i++) {
//         cmd = cmds[i];
//         app[cmd] = (function (cmd) {
//             return (function (str, time) {
//                 time = time || +new Date;
//                 app.raw_tags.push([cmd, str, time]);
//             });
//         }(cmd));
//     }
//     app.start("page");
    
//     app.dom_load_ts = null;
//     app.first_interaction_ts = null;
//     app.dom_ready = function () {
//         var intrvl, ready = false;

//         function fn() {
//             clearInterval(intrvl); intrvl = 0;
//             if (!ready) { ready = true; edetach('load', fn, false); }
//             app.dom_load_ts = app.dom_load_ts || +new Date;
//             console.log('dom load time', app.dom_load_ts);
//         }

//         eattach('load', fn, false);
//         if (addEventListener)
//             d.addEventListener('DOMContentLoaded', fn, false);
//         else if (w.attachEvent && self == self.top)
//             intrvl = setInterval(function () {
//                 try { if (d.body) { d.documentElement.doScroll('left'); fn(); } } catch (x) {}
//             }, 30);
//     };
//     app.first_interaction = function () {
//         var events = 'mousemove keydown mousewheel mousedown scroll'.split(' '), fns = [], i;

//         function fn () {
//             app.first_interaction_ts = app.first_interaction_ts || +new Date;
//             console.log('removing self: ', app.first_interaction_ts - app.dom_load_ts, ' - ', app.first_interaction_ts);
//             for (i=0; i<events.length; i++)
//                 edetach(epre+events[i], fn, false);
//         }
//         for (i=0; i<events.length; i++)
//             eattach(epre+events[i], fn, false);
//     };
    
//     // todo: this shoudl only be done after dom load.
//     app.dom_ready();
//     app.first_interaction();
// })(window,
//    document,
//    window.attachEvent || window.addEventListener,
//    window.detachEvent || window.removeEventListener,
//    window.attachEvent ? 'on' :'');
(function (log, app, w, d, undefined) {
    app.utils = {
        add_listener: function (el, sType, fn, capture) {
	    if (el.addEventListener) {
	        el.addEventListener(sType, fn, (capture));
	    } else if (el.attachEvent) {
	        el.attachEvent("on" + sType, fn);
	    }
        },
        extend: function (src, des) {
            for (var i in src)
                if (src[i])
                    des[i] = src[i];
        },

        cookies: {
            // to measure the full request time.
            set_mark: function (evt, tm) {
                app.utils.cookies.write( "_phct", evt + "&" + (tm || +new Date), 60000);
            },
            get_mark: function () {
                var c = app.utils.cookies.readAndErase('_phct');
                
                if (!c)
                    return false;
                return parseInt(c.split('&')[1]);
            },
            
            // http://www.quirksmode.org/js/cookies.html
            read: function (name) {
                var nameEQ = name + "="
                , ca = document.cookie.split(';')
                , i
                ;
                for(i=0;i < ca.length;i++) {
                    var c = ca[i];
                    while (c.charAt(0)==' ') c = c.substring(1,c.length);
                    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
                }
                return null;
            },
            write: function (name, value, ms) {
                var date
                , expires
                ;
                if (ms) {
                    date = new Date();
                    date.setTime(date.getTime() + ms);
                    expires = "; expires="+date.toGMTString();
                } else {
                    expires = "";
                }
                document.cookie = name+"="+value+expires+"; path=/";
            },
            erase: function (name) {
                this.write(name, '', -1);
            },
            readAndErase: function (name) {
                var val = this.read(name);
                if (val) this.erase(name);
                return val;
            }
        },

        /**
         * The url legth for requests is limited. So check the URL lenght to be
         * within 2000 else send error to server. 
         * 
         * @see http://www.boutell.com/newfaq/misc/urllength.html
         * @see http://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-an-url
         * 
         * On tracking accross domains.
         * @see http://stackoverflow.com/questions/216430/cross-domain-user-tracking
         * @see http://code.google.com/speed/page-speed/docs/rtt.html#AvoidRedirects
         * 
         * Performance measures.
         * @see https://dvcs.w3.org/hg/webperf/raw-file/tip/specs/NavigationTiming/Overview.html
         * @see http://www.theautomatedtester.co.uk/blog/2010/selenium-webtimings-api.html
         */
        send_beacon: function (url, data) {
            var res='';

            for (var i in data) {
                var v = (typeof data[i] == 'object') ? JSON.stringify(data[i]) : data[i];
                res += i + '=' + v + '&';
            }

            var script = d.createElement("script")
            , head = d.getElementsByTagName("head")[0] || d.documentElement
            ;

            script.setAttribute("src", url+'?'+res);
            head.insertBefore(script, head.firstChild);
        }
    };
})(console.log, _phc, window, document);

(function (log, app, w, d) {
    function generate_tags(ts) {
        var r = app.utils.cookies.get_mark();

        app.start('whole', r || ts.page_start );

        if (r && r < ts.page_start) {
            app.start('req', r);
            app.end('req', ts.page_start);
        }

        app.start('page', ts.page_start);
        app.start('body', ts.page_start);
        app.end('body', ts.body_end);
        app.end('page', ts.dom_load_ts);
        // app.start('interaction', ts.body_end);
        // app.end('interaction', ts.first_interaction_ts);

        // comment if done on unload
        app.end('whole', ts.dom_load_ts);

    };

    app.auto = {
        generate_tags: generate_tags
    };
})(console.log, _phc, window, document);




(function (log, app, w, d) {
    var cmds = ["start", "end", "event"], cmd, i, len;
    
    app.raw_tags = app.raw_tags || [];
    
    for (i=0, len=cmds.length; i<len; i++) {
        cmd = cmds[i];
        app[cmd] = (function (cmd) {
            return (function (str, time) {
                time = time || +new Date;
                app.raw_tags.push([cmd, str, time]);
            });
        }(cmd));
    }
    // modifying the end function to send beacon at the end.
    // if the end closes the hierarchy, send the beacon.
    function check_end(str, time) {
        var starts = 0, ends = 0, tags, len, i;
        tags = app.raw_tags;
        for (i=0, len=tags.length; i<len; ++i) {
            if (tags[i][0] == 'start') {
                starts += 1;
            } else if (tags[i][0] == 'end') {
                ends += 1;
            }
        }
        
        if (starts && starts == ends) {
            if (app.send_events) {
                setTimeout(app.send_events, 0);
            } else {
                app.tags_complete = true;
            }
            return true;
        }
        return false;
    };

    if (!check_end()) {
        var old = app.end;
        app.end = function (str, time) {
            old(str, time);
            check_end();
        };
    }

  // todo: parameterized function, which takes the particular measured project.

  /*
   * first time to be registered will be used as the ref_time for any
   * even not being a time span.
   * 
   */

    (function () {
        var uid = +new Date, // only at time of initialization, once.
            data_ref = null, //current node to which childrens will be added.
            last_tag = [],
            ref_time,
            arr = [],
            paths = {},
            fns,
            data = {};          //the root of the datastructure.
        // todo: could make the functions handle multiple tags in
        // the same time. could be coma separated.
        fns = {
            actual_start: function ( tag_str, time ) {
                var tags = tag_str.split(',')
                , lt = last_tag
                , node
                , path
                , len
                , i
                ;
                
                time = time || +new Date;
                if (lt.length == 0) ref_time = time;

                node = {name:tag_str, childrens:[]};
                if (lt.length === 0) {
                    data = node;
                } else {
                    data_ref.push(node);
                }
                data_ref = node.childrens;

                for (i=0, len=tags.length; i<len; i++) {
                    lt.push(tags[i]);
                    path = lt.join('/');
                    paths[path] = {uid: uid, time: time, node:node};
                }
                return;
            },
            actual_end: function ( tag_str, time ) {
                var lt     = last_tag
                // , paths    = paths
                , path     = lt.join("/")
                , tag      = lt.pop()
                , ref_time = (paths[path] && paths[path].time) || ref_time
                , diff
                ;

                if (tag) {
                    diff = (time || +new Date) - ref_time;
                    arr.push([path, uid, diff]);
                    paths[path].node.val = diff;
                    if (lt.length > 0) {
                        data_ref = paths[lt.join('/')].node.childrens;
                    }
                }
                return;
            },
            actual_event: function (tag_str, time) {
                var path = 'page/event/'+tag_str;
                arr.push([path, uid, (time - ref_time) || (+new Date - ref_time)]);
                return;
            }
        };
        
        app.process_tags = function () {
            var tag, i, len;
            for (i=0, len=this.raw_tags.length; i<len; i++) {
                tag = this.raw_tags[i];
                fns["actual_"+tag[0]].apply(this, tag.splice(1));
            }
            app.data = data;
        };
     })();

    
    function calculate_params() {
        app.callback_fn && app.callback_fn(); // todo: figure out what to use this for!

        var B = BrowserDetect, 
            bt = B.browser + '-' + B.version + ':' + B.OS;
        
        return {
            bt: bt,     //this needs to be detected.
            ph_id: _phc.ph_id, //this needs to come from the client site (ex: project no assigned)
            data: app.data
        };
    };

    function is_empty_obj(obj) {
        for (var k in obj) {
            return false;
        }
        return true;
    };
     


    (function () {
        function safe_once(fn) {
            var done = false;
            function ret () {
                try {
                    if (done) {
                        return null;
                    }
                    done = true;
                    return fn();
                } catch (x) {
                    // alert(x, x.stack);       //the heck, no alerts.
                    return null;
                }
            }
            return ret;
        }
        
        function send_events() {
            if (app.auto_tags) {
                app.auto.generate_tags(app.ts);
            }
            app.process_tags();
            if (is_empty_obj(_phc.data)) {
                return;
            }
            var server = (typeof app_state == 'undefined' || app_state == 'live') ? 'perf-hier.appspot.com' : 'localhost:8080';
            // var server = (app_state && app_state == "dev") ? 'localhost:8080' : 'perf-hier.appspot.com';
            app.utils.send_beacon('http://'+server+'/api/register_event', calculate_params());
        };
        app.send_events = safe_once(send_events);

        if ((app.ts && app.ts.dom_load_ts) || app.tags_complete) {
            // dom ready. send the beacon
            setTimeout(app.send_events, 0);
        } else {
            // the top code should run it in case of auto_tags
            // otherwise the end function should catch it.
        }

        function unload_fn() {
            app.utils.cookies.set_mark('req');
        };
        app.utils.add_listener(w, "unload", unload_fn);
        app.utils.add_listener(w, "beforeunload", unload_fn);
    })();



     
})(console.log, _phc, window, document);


// todo: have to think about how to skip certain parts of page
// from the measures.ex: substract the sub parts contribution
// from all of the parts above in hierarchy.

// todo: could there be selective measurements from pages with
// all of them going to separate project.

// todo: look into code by andrea.giammarchi for serializing JSON
// objects.  need it to store the front-end database and also
// events on it to save on changes.

// todo: the requests for statistics could also have long expires
// except the latest once (ex last hour once).
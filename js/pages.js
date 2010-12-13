// idea: automation - ex: shorcuts defined by users.
// plugins for page: notice.


(function ($, dbg, app) {
    var $nav_dom = $('#navigation');
    
    function opts_to_ds(opts) {
        var ret = {};

        if (opts == {}) {
            dbg.warn('got to a has in the end: shouldnt happen');
            return {};
        }

        if ($.isPlainObject(opts)) {
            $.each(opts, function (key, val) {
                ret[key] = opts_to_ds(val);
            });
        } else if ($.isArray(opts)) {
            $.each(opts, function (idx, val) {
                ret[val] = {};
            });
        }

        return ret;
    };

    function url_ds(url, url_options) {
        var parts = app.util.strip(url, '/').split('/')
        , ds = {}
        , last, c, i
        ;
        
        last = ds;

        for (i=0; i<parts.length; i++) {
            c = parts[i];

            if (/^:/.test(c)) {
                break;
            }

            last[c] = {};
            last = last[c];
        }

        $.extend(last, opts_to_ds(url_options));

        return ds;
    };
    
    function indent(content, level) {
        var pre = "", i;
        if (level == undefined) {
            level = content;
            content = '';
        }
        for(i=0;i<level;i++) {
            pre += "&nbsp;";
        }

        if (typeof(content) === 'string') {
            return pre + content;
        } else {
            return content.before($('<span>',{
                html: pre
            }));
        }
    }

    /**
     * Converts a hirarchy of tags to hierarchy with leaves having the url of
     * path to them. Also changes the ds to have attributes like 'html' and 
     * 'childrens' etc.
     */
    function nav_data(ds, params, path, depth) {
        path = path || '/';
        depth = depth || 0;

        if ($.isEmptyObject(ds)) {
            return ds;
        }

        $.each(ds, function (key, val) {
            var npath = app.util.slashify(path, key);
            ds[key] = {
                html: app.util.supplant(key, params),
                childrens: nav_data(val, params, npath, depth+1),
                depth: depth,
                path: npath
            };
        });
        
        return ds;
    };

    function to_name(key) {
        var res = app.util.slashify_nonalpha(key);
        return app.util.strip(res, '/');
    }

    function new_nav(ds, node) {
        var nav, li, uls;

        if ( $.isEmptyObject(ds) ) {
            return '';
        }

        nav = $('<ul>');

        $.each(ds, function (key, val) {
            var li, ul;
            if ($.isEmptyObject(val.childrens)) { // leaf entry
                li = $('<li>', {
                    name: to_name(key),
                    html: $('<a>', {
                        href: app.url.get_string({url: val.path}),
                        html: indent(unescape(val.html), val.depth+1)
                    })
                });
            } else {            // expandable
                li = $('<li>', {
                    'class':'expansion',
                    name: to_name(key),
                    html: indent('+&nbsp;'+unescape(val.html), val.depth)
                });
                ul = new_nav(val.childrens).hide() ;
            }
            nav.append(li);
            if (ul) {
                nav.append(ul);
            }
        });

        return nav;
    };
     
     function update_nav(nav, ds) {
        // find the base, and then create and append the new nav there
        $.each(ds, function (key, val) {
            var n = nav.find('li[name='+to_name(key)+']');
            if (n.length) {
                if (n.length>1) {
                    dbg.warn('heck, how can there be more than one ?', n.length, n);
                }
                update_nav(n.next(), val.childrens);
            } else {
                nav.append( new_nav(ds).children() );
            }
        });
    }

    $nav_dom.delegate('li', 'click', function (event) {
        $(this).html(function (i, h){
            var exp = $(this).next().filter('ul');
            // dont use async operations here, ex: slideDown, slideUp
            if (exp.is(':hidden')) {
                exp.show();
                return h.replace('+', '--');
            } else {
                exp.hide();
                return h.replace('--', '+');
            }
        });
        event.stopPropagation(); //dont disable default. cause anchor tags need to work.
    });

    function _add(url, url_options, params) {
        update_nav( $nav_dom,
                    nav_data( url_ds(url, url_options),
                              params));
    };

    function collapse($els) {
        $els.each(function () {
            var exp = $(this).next().filter('ul');
            if (!exp.is(':hidden')) {
                $(this).click();
            }
        });
    }

    function _show(url) {
        var parts = app.util.strip(url, '/').split('/'),
            curr = $nav_dom, i, e;
        
        for (i=0; i<parts.length; i++) {
            curr = curr.children('li[name='+to_name(parts[i])+']');
            collapse(curr.siblings('li').andSelf());

            curr.click();
            curr = curr.next();
        }
    };

    function _remove(url) {
        var root = app.util.path_root(url)
        , e = $nav_dom.children('li[name='+to_name(root)+']')
        ;
        dbg.warn('root: ', root, url, e);

        e.next().andSelf().remove();
    };

    $(window).bind('hashchange', function () {
        var url = $.bbq.getState('url');

        if (app.routes.has_route(url)) {
            dbg.warn('A: hashchage', url);
            app.controller.invoke(url);
            app.controller.previous_page = app.controller.current_page;
            app.controller.current_page = url;
        } else {
            // todo: show a 404 page.
        }
    });

     app.navigation = {
        add: _add,
        show_only_path: _show,
        remove: _remove
    };
})(jQuery, debug, _ph);


// (function ($, dbg, app) {
//     var before_queues = {
//         all : [],
//         index : []
//     }
//     , after_queues = {
//         all: [],
//         index : []
//     }
//     ;

//     function _add(fn, queue_type, url) { //before => true
//         var queue = queue_type ? before_queues : after_queues
//         , applies_to = false
//         , idx
//             , i
//         ;

//         if ($.isArray(url)) {
//             applies_to = url;
//         } else if (url) {
//             applies_to = [url];
//         }

//         if (!applies_to) {
//             queue.all.push(fn);
//         }

//         idx = queue.index;
//         for (i in applies_to) {
//             url = applies_to[i];
//             idx[url] = idx[url] || [];
//             idx[url].push(fn);
//         }
//         // dbg.log('applies to: ', applies_to || 'all',
//         //         before_queues, after_queues);
//     }

//     function _call(url, page, queue_type) {
//         var queue = queue_type ? before_queues : after_queues
//         , applies_to
//         , ret
//         , fn
//         , i
//         ;

//         for (i in queue.all) {
//             fn = queue.all[i];
//             if (fn(url, page) === false) { //dont care about undefined
//                 return false;
//             }
//         }

//         for (i in queue.index[url]) {
//             fn = queue.index[url][i];
//             if (fn(url, page) === false) {
//                 return false;
//             }
//         }
//         return true;
//     }

//     function add_before(fn, url) {
//         _add(fn, true, url);
//         // dbg.log('inside before', url);
//     };
//     function add_after(fn, url) {
//         _add(fn, false, url);
//     };
//     function call_before(url, page) {
//         // dbg.log('calling before:', url, page);
//         return _call(url, page, true);
//     };
//     function call_after(url, page) {
//         // dbg.log('calling after', url, page);
//         return _call(url, page, false);
//     };

//     app.wrappers = {
//         add_before    : add_before,
//         add_after   : add_after,
//         call_before : call_before,
//         call_after  : call_after
//     };
//     dbg.log(app.wrappers);
// })(jQuery, debug, _ph);

(function ($, dbg, app) {
    var Controller = (function () {

        var notice = null;

        function check_state() {
            var state = $.bbq.getState();

            if (!_ph.controller.current_page && state.url) {
                _ph.url.load(state);
                $(window).trigger('hashchange');
            }
        };

        function _add(url, url_options, cb_fn, params, dontshow) {
            var matches = url.match(/\/\:\w+/g)
            , name
            , len
            , m
            , i
            ;
            // check if the same no of options r there in url_options.
            // check for cb_fn. jQuery type check.
            // push into the array.
            // todo: if options not given, then dont show the url in
            // navigation.

            if (!matches) {
                // check for the type to be function.
                cb_fn = url_options;
                url_options = null;
                matches = [];
            }
            if (!cb_fn) {
                dbg.log('Callback function for page was not defined');
                return false;
            }

            for (i=0, len=matches.length; i<len; i++){
                m = matches[i],
                name = m.substring(2,m.length);

                if (!url_options[name]) {
                    // dbg.log('Options for dynamic variable are not given.');
                    // return false;
                }
            }

            app.routes.add(url, cb_fn);

            if ( !dontshow ) {
                app.navigation.add(url, url_options, params);
            }
            // pages.push(url, url_options, cb_fn);

            check_state();

            return true;
        };

        function _call(url, params) {
            var ret = app.routes.route(url)
            , $ele = $('#content').html('')
            , args
            ;

            dbg.warn('A: call: ', url, notice);
            $('#notice').html(notice);
            notice = '';        // reset notice each time.

            args=[$ele].concat(ret.params);
            app.navigation.show_only_path(url);
            ret.fns.page.apply(this, args);

            return true;
        };

        function _remove(url) {
            app.routes.remove(url);
            app.navigation.remove(url);
        }

        function _test() {
            Controller.add('/a/:url', {url:['a', 'b']}, console.log);
            Controller.invoke('/a/theheck');
        };

        return {
            current_page: null,
            
            add: _add,
            invoke: _call,
            remove: _remove,
            test: _test
        };
    })();

    app.controller = Controller;
})(jQuery, debug, _ph);

(function ($, dbg, app) {
    var Routes = (function () {
        var routes = []
        , orig_routes = []
        ;

        function _add(url, obj) {
            var params=[]
            ;

            orig_routes.push(url);
            url = url.replace(/\/\:\w+/g, function(){
	        var name;
	        name = arguments[0].substring(2,arguments[0].length);
                params.push(name);
	        return '\/([^\/]+)';
            });

            if ($.isFunction(obj)) {
                obj = { page : obj };
            }

            routes.push([RegExp('^'+url+'$'), obj, params]);
        };

        function _remove(url) {
            var i
            , pattern
            ;

            url = app.util.path_root(url);

            for (i=0; i<routes.length; i++) {
                pattern = app.util.path_root(orig_routes[i]);
                if (pattern === url) {
                    routes[i][0] = /nothing/; // essentially it should not match with any route.
                    orig_routes[i] = '/nothing/';
                }
            }
        };

        /**
          * Finds outs the best fit based on these assumptions.
          * 1) all params are separated by /
          * 2) best match is the one with least no of regexp matches.
          *
          * Because of best match thingi, doesnt matter in which order
          * routes are added.
          *
          * @param url the url based on which the routing is done.
          * @returns [obj, params] where obj is the object associated
          *          with the url. And params a dict of matches found.
          *          If no match found, Undefined is returned.
          */
        function _route(url) {
            var pattern, i, matches=[], match, best,
            params, r, l;

            for (i=0; i<routes.length; i++) {
                // Figure out the most specific match.
                pattern = routes[i][0];
                if (pattern.test(url)) {
                    match = url.match(pattern);
                    if (!best || (match.length<best[1].length)) {
                        params = match.slice(1);
                        best = [routes[i], match];
                    }
                }
            }
            return best && {'fns': best[0][1], 'params':params};
        }

        function _check(url) {
            return _route(url) ? true : false;
        };

        function _test() {
            var urls = ['/a/b', '/a/b/', '/c/v', '/as/as/as']
            , routes = ['/:va/:vb/:vc', '/a/:vb', '/:a/:b', '/c/v']
            , i
            , j
            ;
            for (i in routes) {
                Routes.add(routes[i]);
            }
            for (j in urls) {
                Routes.route(urls[j]);
            }
        }

        return {
            add: _add,
            route: _route,
            remove: _remove,
            has_route: _check,
            test: _test
        };
    })();

    app.routes = Routes;

})(jQuery, debug, _ph);


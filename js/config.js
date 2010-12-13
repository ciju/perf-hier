(function ($, undefined) {
    var assoc = {
        onapi: {},
        onuser: {},
        onproject:{}
    };
    
    window._ph = {
        state: {},
        settings: {
            demoproj: {
                id: 1,
                name: 'testproj'
            },
            gist_url: "http://gist.github.com/611126.js?file="
        },
        paths: {
            about: {
                site: '/about/site',
                stats: '/about/stats',
                details: '/about/details'
            },
            proj: {
                create: '/proj/new',
                del: '/proj/del',
                script: '/proj/src',
                info: '/proj/info',
                select: '/proj/select'
            },
            stats: {
                show: '/stats for {project_name}/:dimention/:metric',
                meta: '/stats for {project_name}/:span/:dimention/:metric'
            },
            nometrics: '/nometrics'
        },
        util: {
            strip: function (orig, str) {
                // removes the 'str' from start and end of 'orig' 
                str = str || ' +';
                var start = '^'+str,
                    end = str+'$';
                return orig.replace(RegExp(start), '').replace(RegExp(end), '');
            },
            normalize_space: function (orig) {
                return _ph.util.strip(orig.replace(/ +/g, ' ').replace(/[\n\t]+/g, ' '));
            },
            path_root: function (path) {
                return _ph.util.strip(path, '/').split('/')[0];
            },
            slashify_nonalpha: function (str) {
                return str.replace(/[^a-zA-Z0-9\.-]/g, '_').replace(/_+/g, '_').replace(/_+$/, '');
            },
            slashify: function () {
                var args = Array.prototype.splice.call(arguments, 0)
                , nargs = []
                , i
                , s
                ;
                for (i=0; i<args.length;i++) {
                    s = _ph.util.strip(args[i], '/');
                    if (s) {
                        nargs.push(s);
                    }
                }
                return '/' + nargs.join('/');
            },
            on_all: function ( events, id, fn ) {
                var evnts = events.split(',');

                if (fn === undefined) {
                    fn = id;
                    id = undefined;
                }

                function _on_all(evnts) {
                    var event;
                    if ( evnts.length === 0 || evnts[0] == undefined ) {
                        fn();
                        return;
                    }
                    event = 'on' + $.trim( evnts[0] );

                    _ph.util[event](function () {
                        _on_all( evnts.slice(1) );
                    });
                }
                _on_all( evnts );
            },
            onapi: function (fn) {
                if (typeof(_ph.api) != 'undefined') {
                    fn(_ph.api);
                }
                
                $.subscribe('/ph/api/available', fn);
            },
            onuser: function (fn) {
                if (_ph.current_user) {
                    fn(_ph.current_user);
                }

                $.subscribe('/ph/user/state', function (user) {
                    if (user) fn(user);
                });
            },
            onanon: function (fn) {
                if (_ph.current_user === null) {
                    fn(_ph.current_user);
                }
                $.subscribe('/ph/user/state', function (user) {
                    if (!user) fn(user);
                });
            },
            isanon: function () {
                return _ph.state.user === null;
            },
            ondemo: function (fn) {
                // todo: finish this fn.
                $.subscribe('/ph/about/demo', function (user) {
                    fn();
                });
            },
            onproject: function (fn) {
                if (_ph.state.project && _ph.state.project.id) {
                    fn(_ph.state.project.id);
                }
                
                $.subscribe('/ph/project/select', fn);
            },
            // onproject: function (fn, events) {
            //     if (_ph.state.project && _ph.state.project.id) {
            //         console.warn('didnt ');
            //         fn(_ph.state.project.id);
            //         _ph.util.onproject = function (fn, events) {
            //             console.warn('what the heck');
            //             $.subscribe('/ph/project/select', fn);
            //         };
            //     }
                
            //     $.subscribe('/ph/project/select', fn);
            //     console.warn('onproject: ', events);
            // },
            values: function (k /*, and values */) {
                return typeof k === "function"
                    ? k.apply(this, Array.prototype.slice.call(arguments, 1))
                    : arguments[1];
            },
            supplant: function (str, o) {
                return str.replace(/{([^{}]*)}/g, function (a, b) {
                    var r = o[b];
                    return typeof r === 'string' || typeof r === 'number' ? r : a;
                });
            },
            notify: function (msg) {
                var notice = $('#notice');
                if (!msg) {
                    notice.html('').slideUp();
                    return;
                }

                notice.append($('<div>', {
                    html: $('<a>', {
                        href: 'javascript:;',
                        html: msg,
                        click: function (ele) {
                            console.warn('inside click', ele );
                            notice.slideUp();
                            return false;
                        }
                    })
                })).slideDown();
            },
            loading: {
                start: function () {
                    _ph.util.notify('loading..');
                },
                end: function () {
                    _ph.util.notify();
                }
            }
        }
    };

    
    // String.prototype.supplant = function (o) {
    //     return this.replace(/{([^{}]*)}/g, function (a, b) {
    //         var r = o[b];
    //         return typeof r === 'string' || typeof r === 'number' ? r : a;
    //     });
    // };

    if (app_state != 'dev') {
        _ph.settings.demoproj.id = 61007;
    }

})(jQuery);

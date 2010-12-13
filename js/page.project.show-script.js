(function ($, dbg, app) {

     
    /**
     * Ugly hack stats here. Rewriting the document.write because of githubs 
     * embed ugliness.
     */
    var orig = document.write
    , gists = {}
    , args = []
    , css_done = false
    ;

    document.write = function (arg) {
            /.*gist.github.com.*/.test(arg) ? args.push(arg) : orig(arg);
    };
    
    function get_client_code(file, fn) {
        var src = app.settings.gist_url + file;

        if (gists[src]) {
            setTimeout(function () {
                if (!css_done) {
                    fn(gists['css']);
                    css_done = true;
                }
                fn(gists[src]);
            }, 0);
            return;
        }

        $.getScript(src, function () {
            var exp = new RegExp(file);
            for (var i=0; i<args.length; i++) {
                if (!css_done && /\.css/.test(args[i])) {
                    css_done = true;
                    fn(args[i]);
                    gists['css'] = args[i];
                }
                if (exp.test(args[i])) {
                    fn(args[i]);
                    gists[src] = args[i];
                    dbg.warn('cahced gist');
                }
            }
        });
    }
    /**
     * Ugly hack ends here.
     */

    function show($ele) {
        var project = app.url.get_state('project');
        if (!project || !project.id) {
            // if no projects, then new needs to be created, else one needs to
            // be selected.
            app.url.load(app.paths.proj.select);
            return;
        }

        project = project || {
            id: 1,
            name: 'testproj'
        };

        $('#page_show_script').tmpl({
            project: project
        }).appendTo($ele);

        css_done = false;
        $ele.find('.code').each(function () {
            var $this = $(this);
            setTimeout(function () {
                get_client_code($this.attr('id'), function (stuff) {
                    $this.append($(stuff.replace('REPLACE_WITH_PHC_PROJECT_ID', project.id)));
                });
            }, 0);
        });

        $('#custom_code_helper a').click(function () {
            $('#custom_code_helper').hide();
            $('#top_code').show();
        });

        $('#top_code a').click(function () {
            $('#top_code').hide();
            $('#custom_code_helper').show();
        });

    }

    app.util.onuser(function () {
        app.controller.add(app.paths.proj.script, show);
    });
})(jQuery, debug, _ph);



// (function () {
//     window._phc = {};
//     var cmds = ["start", "end", "event"],
//     cmd, i, len;
//     _phc.raw_tags = _phc.raw_tags || [];
//     for (i=0, len=cmds.length; i<len; i++) {
//         cmd = cmds[i];
//         _phc[cmd] = (function (cmd) {
//             return (function (str, time) {
//                 time = time || +new Date;
//                 _phc.raw_tags.push([cmd, str, time]);
//             });
//         }(cmd));
//     }
// }());
// _phc.start("page");

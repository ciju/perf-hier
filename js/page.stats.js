/**
 * The statistics for metrices.
 */

(function($, dbg, app) {
    function process_data(data) {
        var len
        , labels = ['dates']
        , str = ''
        , i
        , j
        , e
        , v
        , a
        , t
        ;

        for (j in data) {
            len = len || data[j].length;
            labels.push(j);
        }

        // skip all the initial 0 entries.
        for (i=0; i<len; i++) {
            var all0s = true;

            for (j in data) {
                e = data[j][i];
                if (e[1][0] != 0) {
                    all0s = false;
                }
            }

            if (!all0s) {
                break;
            }
        }

        for (i=0; i<len; i++) {
            a = [];
            t = null;
            for (j in data) {

                e = data[j][i];
                if (e && e[1][0]) {
                    t = e[0];
                    a.push(e[1][1]/e[1][0]);
                } else {
                    a.push(null);
                }
            }

            if (t && a.length) {
                str += t + ',' + a.join(',') + '\n';
            }
        }
        return { labels: labels, csv: str };
    };

    function convert_to_tree(ds) {
        var tree = {}
        , i
        ;

        function make_path(root, path, val) {

            if (!path.length) return;

            var nname = path.shift();

            if (!root.name) {
                root.name = nname;
                root.childrens = {};
            }

            if (!path.length) {
                root.val = val[1]/val[0];
            }

            if (!path.length) return;

            if (root.childrens[path[0]] == null) {
                root.childrens[path[0]] = {};
            }

            make_path(root.childrens[path[0]], path, val);
        };

        for (i in ds) {
            make_path(tree, i.split('/'), ds[i]);
        }

        return tree;
    };

    function actions(acts, params, fn, failure_fn) {
        var res_hash = {}
        , done = {}
        , failed = false
        ;

        function check_done() {
            var i, all_done = true;
            for (i=0; i<acts.length; i++)
                if (!done[acts[i]])
                    all_done = false;
            return all_done;
        }

        function gather_res() {
            var i, res = [];
            for (i=0; i<acts.length; i++)
                res.push(res_hash[acts[i]]);
            return res;
        }
        
        $.each(acts, function (i, a) {
            done[a] = false;
            app.api[a]( params, function (data) {
                done[a] = true;
                res_hash[a] = data;
                
                if (!failed && check_done()) {
                    fn(gather_res());
                }
            }, function () {
                // dbg.warn('failed with:', a);
                failed = true;
                failure_fn();
            });
        });
    }

    // this has to be invoked after the api is initialized.
    var plot_charts = function ($ele, metric) {
        var params
        , types = {
            timeline: null,
            hierarchy: null
        }
        ;

        // metric =  metric || '/general/aggregate';
        // project = app.state.project.id || 1;

        params = {
            // metric: metric || '/general/aggregate',
            project: (app.state.project && app.state.project.id),
            typ: metric || 'aggregate/general'
        };

        if (!params.project) {
            // todo: do something
        }

        if (metric == 'metrics/empty') {
            // todo: this has to be better handled.
            // may be a 404 page, with the functionality of cusom messages.
            // or may be even redirect back to the revious page with a notice.
            $ele.html('No metrics yet :(');
            return;
        }

        app.util.loading.start();

        function show_stats(stats) {
            var $plots = $('<div id="ph_plots" style="position:relative;">')
            , $ring  = $('<div id="ph_hierring" style="float:right">')
            , $tl    = $('<div id="ph_timeline" style="float:right">')
            ;

            app.util.loading.end();

            // check for empty timeline.
            if ($.isEmptyObject(stats[0])) {
                $ele.html('No data available for the particular dimentions, for this month');
            }

            app.phTimeline(
                process_data(stats[0])
            ).appendTo($tl);

            app.phChart(
                convert_to_tree(stats[1])
            ).get_div().appendTo($ring);
            
            $plots.append($tl).append($ring).appendTo($ele);
        }

        function error_page() {
            $ele.html('Something wrong happened.');
        }

        actions(['get_csv_timelines', 'get_aggregate_metrics'], params, show_stats, error_page);
    };


    function show_page($ele, dim, met) {
        plot_charts($ele, [dim, met].join('/'));
    };
    
    var showing_project = null;
    
    function setup_nav_and_page(proj, path) {
        // cleanup existing stats route and navigation.
        app.controller.remove(path);

        app.util.notify('loading..');
        app.api.get_metric_tags({
            project: proj.id
        }, function (metrics) {
            app.util.notify();
            // todo: change the add function so that parameters
            // are passed as such, rather than a hash.
            if ($.isEmptyObject(metrics)) {
                // go back to the previous page, with an allert.
                dbg.warn('empty metrics');
                showing_project = null;
                app.util.notify('It might take an hour or two to aggregate the project statistics.');
                app.url.load(app.paths.proj.select);
                return;
            }
            
            app.controller.add(path
                               , metrics
                               , show_page
                               , {
                                   project_name: proj.name
                               });
        }, function (msg) {
            app.url.load(app.paths.proj.select);
        });
        
    };


    function show_nometrics($ele) {
        $ele.html('Couldnt find the stats. If you just created the project, '+
                  'please wait for an hour or two to see the results.');
    };
    app.controller.add(app.paths.nometrics, show_nometrics, $.noop, {}, true);

    app.util.on_all('api, user, project', function () {
        if (showing_project == app.state.project.id) {
            return;
        }
        showing_project = app.state.project.id;

        setup_nav_and_page(app.state.project, app.paths.stats.show);
    });
    
    app.util.on_all('api, demo', function () {
        app.url.load({
            url: app.paths.proj.select,
            project: app.settings.demoproj
        });
        $.publish('/ph/project/select', app.settings.project);
        setup_nav_and_page(app.settings.demoproj, app.paths.stats.show);
    });

})(jQuery, debug, _ph);

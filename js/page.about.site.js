(function ($, dbg, app) {
    function show($ele) {
        $('#about_site').tmpl({}).appendTo($ele);
        $('#help-login').hide();
        $('#demolink').click(function () {
            $.publish('/ph/about/demo');
        });
    }

    app.util.onanon(function () {
        dbg.warn('anon');
        app.url.load(app.paths.about.site);
        $('#help-login').show();
        $('#help-create').hide();
    });

    
    app.controller.add(app.paths.about.site, show);

})(jQuery, debug, _ph);


(function ($, dbg, app, undefined) {
     app.controller.add(app.paths.about.stats, function ($e) {
         $('#about_stats').tmpl({}).appendTo($e);
     });
 })(jQuery, debug, _ph);

(function ($, dbg, app) {
    app.controller.add(app.paths.about.details, function ($e) {
        $('#about_details').tmpl({}).appendTo($e);
    });
})(jQuery, debug, _ph);



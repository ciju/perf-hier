(function ($, dbg, app) {

    if (!$.param) {
        dbg.error('BBQ needs to be loaded before this');
    }
    
    $.param.fragment.noEscape('{}[]/');
    
    function getStateURL (state) {
        return $.param.fragment('/', state);
    };

    function update_url(state) {

        if ( (!_ph.state.project && state.project && state.project.id)
             || (state.project && (parseInt(state.project.id) != parseInt(app.state.project.id)))) {

            app.state.project = {};
            $.extend(app.state.project, state.project);

            $.publish('/ph/project/select', app.state.project);
        }
        dbg.info('A: update: ', state.url);
        $.bbq.pushState(state);
    };

    app.url = {
        get_string: function (state) {
            return getStateURL($.extend({}, app.state, (state || {})));
        },
        load: function (url, notice) {
            dbg.info('A: load ', url, app.state.url, notice);
            
            $.extend(app.state, (typeof url === 'string') ? {url: url} : url || {});
            update_url(app.state);
        },
        get_state: function (key) {
            return $.bbq.getState(key);
        }
    };

})(jQuery, debug, _ph);
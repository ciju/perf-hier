/**
 * Page to create new projects.
 */

(function ($, dbg, app) {

    var $tmpl = 
        $("<div>"+
          " <form>" +
          "  <label for='proj_name'>Project Name</label>"+
          "  <input type='text' id='proj_name' name='proj_name' size='40'>" +
          "  <input type='submit' value='Create' name='create_proj'>"+
          " </form>" +
          "</div>");
    
    function show($ele) {
        var $submit = $tmpl.find('[name=create_proj]');

        function create_proj(e) {

            app.api.post_create_project({
                project: $tmpl.find('#proj_name').val()
            }, function (data) {
                if (data.id) {
                    app.state.project = data;
                    dbg.log('project created: ', app.state.project);
                } else {
                    dbg.warn('some problem with project creation');
                }

                app.url.load({url: app.paths.proj.script,
                                      project: data});

            }, function (err, msg) {
                app.util.notify('This project name is already in use. Please choose another name.');
            });
            return false;
        }
        
        $submit.click(create_proj);     // calls an encapsulation for backend.

        
        $ele.append($tmpl);
    };

    

    app.util.onuser(function (user) {
        app.controller.add(app.paths.proj.create, show);
    });
    
})(jQuery, debug, _ph);

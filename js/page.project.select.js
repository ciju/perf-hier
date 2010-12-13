(function ($, dbg, app) {
    function show($ele) {

        app.api.get_list_of_projects(function (data) {
            var  projects = []
            , selected = false
            , i
            ;

            projects.push({name:'Select project', desc:'', ph_id: '-1'});

            if (data.length == 0) {
                // if user has no projects, direct him to create project page.
                app.url.load(app.paths.proj.create);
                return;
            }
            for (i in data) {
                var proj = {
                    name: data[i].name,
                    desc: data[i].desc,
                    ph_id: data[i].project
                };

                if (app.state && app.state.project && (app.state.project.id == proj.ph_id)) {
                    proj.selected = 'selected';
                    selected = true;
                }
                projects.push(proj);
            }

            if (!selected && projects.length == 2) {
                projects[1].selected = 'selected';
            }

            $('#page_select').tmpl({
                projects: projects
            }).change(function (e) {
                if ( !app.state ) {
                    app.state = {};
                }

                $(this).find("option:selected").each(function() {
                    if ( $(this).val() === '-1' ) {
                        return;
                    }
                    
                    app.url.load({
                        url: app.paths.proj.select,
                        project: {
                            id: $(this).val(),
                            name: app.util.strip($(this).html())
                        }
                    });

                    $.publish('/ph/project/select', app.state.project);
                });
            }).appendTo($ele).change();
            
        });
    }


    app.util.onuser( function () {
        app.controller.add(app.paths.proj.select, show);
    });
})(jQuery, debug, _ph);



(function ($, dbg, app) {
  /*
   * todo: this module needs work. Separate the two 
   * subscriptions. Only api one gives api as paramter.
   */ 
    var subscription,
        sub_to = ['/ph/api/available'];
    
    subscription = $.subscribe_all(sub_to, function (api) {
        api.get_user_info({}, function (info) {
            var name, login;

            app.current_user = info.logged_in ? info.nick : null;
            
            if (info.logged_in) {
                login = info.nick ? '<span class="username">Hi '
                    + info.nick
                    + '</span> | ' : '';
                login += '<a href="/logout">Log Out</a>';
            } else {
                login = '<a href="/login">Log In</a>';
            }
            $('#userbox').html(login);

            dbg.info('publishing user sate: ', app.current_user);
            $.publish('/ph/user/state', app.current_user);
        });
    });
})(jQuery, debug, _ph);


import re
from plogging import log
from inspect import getargspec

from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import db

import models

# return int if possible
def tryint(val):
    try:
        return int(val)
    except:
        return val


def authorized_role(role, kind="", redirect=True, uri=None):
    """
    http://appengine-cookbook.appspot.com/recipe/authorized_role-decorator/
    with slight modifiction for redirection etc by -- ciju

    A decorator to enforce user roles, currently 'user' (logged in)
    'admin' and 'author' (owner of the object to be edited or deleted).
    To use it, decorate your handler methods like this:
    class Add(webapp.RequestHandler):
      @authorized_role("user")
      def get(self):
    url_mapping = "/photos/(.+)/edit"

    instead of:
    class Edit(webapp.RequestHandler):
      def get(self, keyname):
        object = Photo.get_by_key_name(keyname)

    you have:
    class Edit(webapp.RequestHandler):
      @authorized_role("admin, author", "Photo")
      def get(self, object):
        # returns object
    class Delete(webapp.RequestHandler):
      @authorized_role("admin, author")
      def get(self, object):
        object.delete()
    This decorator is applied to a GET handler only because the return
    redirects are done as GETs (not the original HTTP verb for the handler).

    Decorator expects first argument to be object.key() or object.key().name().
    In case of Edit and Delete, decorator will returns object itself.
    """

    def wrapper(handler_method):
        def check_login(self, *args, **kwargs):
            if self.request.method == "GET" or self.request.method == "POST": # ciju: added post check
                obj = None
                self.user = user = users.get_current_user() # ciju: dont know if this is wise! added self.user
                is_admin = users.is_current_user_admin()
                roles = [x.strip() for x in role.split(",")]
                if not user:
                    if redirect == True:
                        self.redirect(users.create_login_url(uri or self.request.uri))
                    else:
                        return
                elif "admin" in roles or "author" in roles:
                    args = list(args)
                    k = tryint(args[0])
                    key = db.Key.from_path(kind, k) if kind else k
                    try:
                        obj = db.get(key)
                    except db.BadKeyError:
                        self.error(500)
                        # self.redirect("/403")
                    finally:
                        if obj and (is_admin or user == obj.author):
                            # switch first argument with an object
                            args[0] = obj
                            return handler_method(self, *args, **kwargs)
                        else:
                            self.error(500)
                            # self.redirect("/403")
                elif "user" in roles:
                    return handler_method(self, *args, **kwargs)
                else:
                    self.error(500)
                    # self.redirect("/403")
            else:
                self.error(500)
                # self.redirect("/403")
        check_login.func_name = handler_method.func_name
        return check_login
    return wrapper


def allowed_for(roles, resources=''):
    """
    """
    def wrapper(handler_method):
        def check_auth(self, *args, **kwargs):
            def copy_and_rm_args(args, kwargs, defaults):
                "map args from kwargs and arg defaults"
                res = []
                dstart = len(args) - len(defaults) # defaults start
                for i, a in enumerate(args):
                    if a in kwargs:
                        res.append(kwargs[a])
                        del kwargs[a]
                    elif i >= dstart:
                        res.append(defaults[i-dstart])
                    else:
                        return False
                return res
            def get_kinds(roles):
                return [x.strip() for x in roles.split(',')]
            def get_object(resource, args, orig):
                # log(resource, orig, args)
                k, t = resource.split('@')
                attr = orig.index(k)
                log(t, k, args)
                # obj = getattr( getattr(models, t), 'get_by_'+k)(args[attr])
                try:
                    obj = getattr( getattr(models, t), 'get_by_'+k)(args[attr])
                except db.BadKeyError:
                    obj = False
                finally:
                    log(args, k, orig, obj)
                    return obj

            def put_object(resource, args, orig, obj):
                k, t = resource.split('@')
                args[orig.index(k)] = obj


            user = self.user = users.get_current_user()
            is_admin = users.is_current_user_admin()
            kinds = get_kinds(roles)
            log(kinds, resources)


            if 'user' in kinds:
                return handler_method(self, *args, **kwargs)

            argspec = getargspec(handler_method)
            required_args = argspec[0][1:]
            defaults = argspec[3] or []
            log(required_args, kwargs, defaults)
            args = copy_and_rm_args(required_args, kwargs, defaults)


            obj = get_object(resources, args, required_args)

            # check based on author attribute, if present
            if 'author' in kinds and getattr(obj, 'author', None):
                # where is the author check done ?
                put_object(resources, args, required_args, obj)
                return handler_method(self, *args, **kwargs)

            # check generic authorization stuff.
            # @see Project for details
            if getattr(obj, 'check_access', None):
                if obj.check_access(user, kinds):
                    put_object(resources, args, required_args, obj)
                    return handler_method(self, *args, **kwargs)

            #     # anon check should be done here.

            if 'admin' in kinds:
                if not is_admin:
                    return {'status': 'not_found'}
                put_object(resources, args, required_args, obj)
                return handler_method(self, *args, **kwargs)

            return {'status': 'not_found'}

        check_auth.func_name = handler_method.func_name
        check_auth.__doc__   = handler_method.__doc__
        return check_auth
    return wrapper


def authorized_role_new(role):
    """

    NOTE: if status specified in the return, the wrapper wont add
    the result hash.
    """
    def wrapper(handler_method):
        def check_login(self, *args, **kwargs):
            required_args = getargspec(handler_method)[0][1:]
            log(args, kwargs, required_args)

            obj = None
            self.user = user = users.get_current_user() # ciju: !
            is_admin = users.is_current_user_admin()
            roles = [x.strip() for x in role.split(",")]
            if not user:
                res = {'status' : 'not_found'}
            elif "admin" in roles or "author" in roles:
                args = list(args)
                log(args, roles)
                k = tryint(args[0]) # incase key is id not name
                key = db.Key.from_path(kind, k) if kind else k
                try:
                    obj = db.get(key)
                except db.BadKeyError:
                    res = {'status' : 'not_found'}
                finally:
                    if obj and (is_admin or user == obj.author):
                        # switch first argument with an object
                        args[0] = obj
                        res = handler_method(self, *args, **kwargs)
                    else:
                        res = {'status' : 'not_found'}
            elif "user" in roles:
                res = handler_method(self, *args, **kwargs)
            else:
                res = {'status' : 'not_found'}
            return res
        check_login.func_name = handler_method.func_name
        check_login.__doc__ = handler_method.__doc__
        return check_login
    return wrapper


def returns_json(f):
    def jsonify_return(self, *args, **kwargs):
        self.response.headers['Content-Type'] = 'text/javascript'
        self.response.out.write( simplejson.dumps( f(self, *args, **kwargs) ) )
    jsonify_return.func_name = f.func_name
    return jsonify_return

def transaction(f):
    return lambda *args, **kwargs: db.run_in_transaction(f, *args, **kwargs)

def prefix_func_name(f):
    def wrapper(cls, req):
        return ['/'+f.func_name+'/'+t+'/' for t in f(cls, req)]
    wrapper.func_name = f.func_name
    wrapper.__doc__ = f.__doc__

    return wrapper



def work_queue_only(func):
  """Decorator that only allows a request if from cron job, task, or an admin.

  Also allows access if running in development server environment.

  Args:
    func: A webapp.RequestHandler method.

  Returns:
    Function that will return a 401 error if not from an authorized source.

    @see copied from hub/main.py in the pubsubhubbub project.
  """
  def decorated(myself, *args, **kwargs):
    if ('X-AppEngine-Cron' in myself.request.headers or
        'X-AppEngine-TaskName' in myself.request.headers or
        is_dev_env() or users.is_current_user_admin()):
      return func(myself, *args, **kwargs)
    elif users.get_current_user() is None:
      myself.redirect(users.create_login_url(myself.request.url))
    else:
      myself.response.set_status(401)
      myself.response.out.write('Handler only accessible for work queues')
  return decorated


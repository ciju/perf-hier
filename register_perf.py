import os
import cgi

print 'Content-Type: text/html'
print ''
print str(dict(os.environ))

form = cgi.FieldStorage()

for f in form.list:
    if f.name[0] == '-':  # take care of '-' in cgi
        f.name = f.name[1:]
    print f.name, f.value


# look at the file metioned below on how to do this. 
# ~/downloads/setups/google_appengine/lib/webob/webob/__init__.py 

# The information needed, has to be communicated b/w this one and
# the backend. There are few which are passed via the post
# variables. Others are infered from the information in
# request. Put all of them into a hash.

# These are then used to create a datastore entry. Fork-join used
# to insert the entry into the datastore. 

# Check performance difference b/w cgi and wsgiref versions.

class Request(object):
    content_types = ['application/x-www-form-urlencoded', ]
    def __init__(env):
        self.env = env

    def method(self):
        pass
    property(method)

    def content_type(self):
        pass
    property(content_type)

# import os
# import sys
# import wsgiref.util

# from google.appengine.ext import db
# from google.appengine.ext import webapp
# import fork_join_queue

# from decorators import authorized_role, returns_json, authorized_role_new, work_queue_only

# # todo: give this a better name!
# class Data(db.Model):
#     # txt = db.StringProperty()
#     time = db.DateTimeProperty(auto_now=True)
#     data = db.TextProperty()
#     work_index = db.IntegerProperty()


# class ComputeAndLogStats(webapp.RequestHandler):

#     FJ_Queue = fork_join_queue.ShardedForkJoinQueue(
#         Data,
#         Data.work_index,
#         '/work/queues',          # the url
#         'fjqueue',               # queue name
#         batch_size         = 15, # may be this could be time based.
#         batch_period_ms    = 500,
#         lock_timeout_ms    = 10000,
#         sync_timeout_ms    = 250,
#         stall_timeout_ms   = 30000,
#         acquire_timeout_ms = 10,
#         acquire_attempts   = 50,
#         shard_count        = 1)


#     @classmethod
#     def __entry_list(self, data, tab_prefix=""):
#         """ take the hierarchical data supplied by client and
#         make a list of tuple of its name and val
#         """
#         if tab_prefix == '':
#             new_prefix = data['name']
#         else:
#             new_prefix = tab_prefix + '/' + data['name']
#         arr = [ (new_prefix, data['val']) ]
#         for c in data['childrens']:
#             arr += self.__entry_list(c, new_prefix)
#         return arr
        
#     @classmethod
#     def calc_stats(cls, req, time, stats):
#         # note: Reservoir sampling with fixed seed random number
#         # generator. Should the samples be taken from sessions or
#         # all. The sharded counter could be used. 
        
#         # todo: check if the request came from one of the sites
#         # registered with the project. and also check the ph_id
#         # if both of them false then bail out.

#         # todo: also need to differentiate based on some id
#         # generated at client, to show a graph, specifically to
#         # somethign tagged over there.

#         ph_id = req.get('ph_id')

#         entries = cls.__entry_list( json.loads(req.get('data')) )
#         cat = Dimentions.get_dimentions_and_metrics(req, time)

#         # todo: need to add prefix and suffix tags.
#         total = [(slashify(ph_id, c[0], e[0], c[1]), e[1]) for c in cat for e in entries]

#         log('total len:   ' + str(len(total)))
#         for i in total:
#             # log(' -- '+str(i[0]) )
#             if i[0] not in stats:
#                 stats[i[0]] = (1, i[1])
#             else:
#                 c, v = stats[i[0]]
#                 stats[i[0]] = (c+1, v+i[1])

#         return stats
        

#     @classmethod
#     def enqueue(cls, req):
#         """Call it to get all the needed params from the logging request. 
#         """
#         widx = cls.FJ_Queue.next_index()
#         Data(data       = json.dumps(Dimentions.get_stats(req)),
#              time       = datetime.datetime.now(),
#              work_index = widx).put()
#         cls.FJ_Queue.add(widx)
#         return
        
#     @work_queue_only
#     def post(self):
#         cls = self.__class__
#         stats = {}
#         work_list = cls.FJ_Queue.pop(self.request)
#         log('--- many: ' + str(len(work_list)))
#         for w in work_list:
#             stats = cls.calc_stats(json.loads(str(w.data)), w.time, stats)

#         StatInfo.update_keys(stats)
#         return
        
 

# # note: what about proxy caching. what about cookies being cached by proxy.

# class ApiRegisterEvent(webapp.RequestHandler):

#     def get(self):
#         ComputeAndLogStats.enqueue(self.request)
#         # todo: return 204 or whatever the code is for no
#         # content.
#         return



# def run_bare_wsgi_app(application):
#   """Like run_wsgi_app() but doesn't add WSGI middleware."""
#   env = dict(os.environ)
#   env["wsgi.input"] = sys.stdin
#   env["wsgi.errors"] = sys.stderr
#   env["wsgi.version"] = (1, 0)
#   env["wsgi.run_once"] = True
#   env["wsgi.url_scheme"] = wsgiref.util.guess_scheme(env)
#   env["wsgi.multithread"] = False
#   env["wsgi.multiprocess"] = False
#   result = application(env, _start_response)
#   if result is not None:
#     for data in result:
#       sys.stdout.write(data)


# def _start_response(status, headers, exc_info=None):
#   """A start_response() callable as specified by PEP 333"""
#   if exc_info is not None:
#     raise exc_info[0], exc_info[1], exc_info[2]
#   print "Status: %s" % status
#   for name, val in headers:
#     print "%s: %s" % (name, val)
#   print
#   return sys.stdout.write



# # TODO #


# # Request: figures out various parameters to log ex: the remote
# # addr, browser type, and query params etc. and passes them on to
# # the handler.

# # Minimalistic response. Return 'No Content'.

# # The data has to be recorded into the datastore. Find out the
# # base datastore api, and use that.
































# class Request(object):

#     ## Options:
#     charset = None
#     unicode_errors = 'strict'
#     decode_param_names = False
#     ## The limit after which request bodies should be stored on disk
#     ## if they are read in (under this, and the request body is stored
#     ## in memory):
#     request_body_tempfile_limit = 10*1024

#     def __init__(self, environ=None, environ_getter=None, charset=NoDefault, unicode_errors=NoDefault,
#                  decode_param_names=NoDefault):
#         if environ is None and environ_getter is None:
#             raise TypeError(
#                 "You must provide one of environ or environ_getter")
#         if environ is not None and environ_getter is not None:
#             raise TypeError(
#                 "You can only provide one of the environ and environ_getter arguments")
#         if environ is None:
#             self._environ_getter = environ_getter
#         else:
#             if not isinstance(environ, dict):
#                 raise TypeError(
#                     "Bad type for environ: %s" % type(environ))
#             self._environ = environ
#         if charset is not NoDefault:
#             self.__dict__['charset'] = charset
#         if unicode_errors is not NoDefault:
#             self.__dict__['unicode_errors'] = unicode_errors
#         if decode_param_names is not NoDefault:
#             self.__dict__['decode_param_names'] = decode_param_names

#     def __setattr__(self, attr, value, DEFAULT=[]):
#         ## FIXME: I don't know why I need this guard (though experimentation says I do)
#         if getattr(self.__class__, attr, DEFAULT) is not DEFAULT or attr.startswith('_'):
#             object.__setattr__(self, attr, value)
#         else:
#             self.environ.setdefault('webob.adhoc_attrs', {})[attr] = value

#     def __getattr__(self, attr):
#         ## FIXME: I don't know why I need this guard (though experimentation says I do)
#         if attr in self.__class__.__dict__:
#             return object.__getattribute__(self, attr)
#         try:
#             return self.environ['webob.adhoc_attrs'][attr]
#         except KeyError:
#             raise AttributeError(attr)

#     def __delattr__(self, attr):
#         ## FIXME: I don't know why I need this guard (though experimentation says I do)
#         if attr in self.__class__.__dict__:
#             return object.__delattr__(self, attr)
#         try:
#             del self.environ['webob.adhoc_attrs'][attr]
#         except KeyError:
#             raise AttributeError(attr)

#     def environ(self):
#         """
#         The WSGI environment dictionary for this request
#         """
#         return self._environ_getter()
#     environ = property(environ, doc=environ.__doc__)

#     def _environ_getter(self):
#         return self._environ

#     def _body_file__get(self):
#         """
#         Access the body of the request (wsgi.input) as a file-like
#         object.

#         If you set this value, CONTENT_LENGTH will also be updated
#         (either set to -1, 0 if you delete the attribute, or if you
#         set the attribute to a string then the length of the string).
#         """
#         return self.environ['wsgi.input']
#     def _body_file__set(self, value):
#         if isinstance(value, str):
#             length = len(value)
#             value = StringIO(value)
#         else:
#             length = -1
#         self.environ['wsgi.input'] = value
#         self.environ['CONTENT_LENGTH'] = str(length)
#     def _body_file__del(self):
#         self.environ['wsgi.input'] = StringIO('')
#         self.environ['CONTENT_LENGTH'] = '0'
#     body_file = property(_body_file__get, _body_file__set, _body_file__del, doc=_body_file__get.__doc__)

#     scheme = environ_getter('wsgi.url_scheme')
#     method = environ_getter('REQUEST_METHOD')
#     script_name = environ_getter('SCRIPT_NAME')
#     path_info = environ_getter('PATH_INFO')
#     ## FIXME: should I strip out parameters?:
#     content_type = environ_getter('CONTENT_TYPE', rfc_section='14.17')
#     content_length = converter(
#         environ_getter('CONTENT_LENGTH', rfc_section='14.13'),
#         _parse_int_safe, _serialize_int, 'int')
#     remote_user = environ_getter('REMOTE_USER', default=None)
#     remote_addr = environ_getter('REMOTE_ADDR', default=None)
#     query_string = environ_getter('QUERY_STRING')
#     server_name = environ_getter('SERVER_NAME')
#     server_port = converter(
#         environ_getter('SERVER_PORT'),
#         _parse_int, _serialize_int, 'int')

#     _headers = None

#     def _headers__get(self):
#         """
#         All the request headers as a case-insensitive dictionary-like
#         object.
#         """
#         if self._headers is None:
#             self._headers = EnvironHeaders(self.environ)
#         return self._headers

#     def _headers__set(self, value):
#         self.headers.clear()
#         self.headers.update(value)

#     headers = property(_headers__get, _headers__set, doc=_headers__get.__doc__)

#     def host_url(self):
#         """
#         The URL through the host (no path)
#         """
#         e = self.environ
#         url = e['wsgi.url_scheme'] + '://'
#         if e.get('HTTP_HOST'):
#             host = e['HTTP_HOST']
#             if ':' in host:
#                 host, port = host.split(':', 1)
#             else:

#                 port = None
#         else:
#             host = e['SERVER_NAME']
#             port = e['SERVER_PORT']
#         if self.environ['wsgi.url_scheme'] == 'https':
#             if port == '443':
#                 port = None
#         elif self.environ['wsgi.url_scheme'] == 'http':
#             if port == '80':
#                 port = None
#         url += host
#         if port:
#             url += ':%s' % port
#         return url
#     host_url = property(host_url, doc=host_url.__doc__)

#     def application_url(self):
#         """
#         The URL including SCRIPT_NAME (no PATH_INFO or query string)
#         """
#         return self.host_url + urllib.quote(self.environ.get('SCRIPT_NAME', ''))
#     application_url = property(application_url, doc=application_url.__doc__)

#     def path_url(self):
#         """
#         The URL including SCRIPT_NAME and PATH_INFO, but not QUERY_STRING
#         """
#         return self.application_url + urllib.quote(self.environ.get('PATH_INFO', ''))
#     path_url = property(path_url, doc=path_url.__doc__)

#     def path(self):
#         """
#         The path of the request, without host or query string
#         """
#         return urllib.quote(self.script_name) + urllib.quote(self.path_info)
#     path = property(path, doc=path.__doc__)

#     def path_qs(self):
#         """
#         The path of the request, without host but with query string
#         """
#         path = self.path
#         qs = self.environ.get('QUERY_STRING')
#         if qs:
#             path += '?' + qs
#         return path
#     path_qs = property(path_qs, doc=path_qs.__doc__)

#     def url(self):
#         """
#         The full request URL, including QUERY_STRING
#         """
#         url = self.path_url
#         if self.environ.get('QUERY_STRING'):
#             url += '?' + self.environ['QUERY_STRING']
#         return url
#     url = property(url, doc=url.__doc__)

#     def relative_url(self, other_url, to_application=False):
#         """
#         Resolve other_url relative to the request URL.

#         If ``to_application`` is True, then resolve it relative to the
#         URL with only SCRIPT_NAME
#         """
#         if to_application:
#             url = self.application_url
#             if not url.endswith('/'):
#                 url += '/'
#         else:
#             url = self.path_url
#         return urlparse.urljoin(url, other_url)

#     def path_info_pop(self):
#         """
#         'Pops' off the next segment of PATH_INFO, pushing it onto
#         SCRIPT_NAME, and returning the popped segment.  Returns None if
#         there is nothing left on PATH_INFO.

#         Does not return ``''`` when there's an empty segment (like
#         ``/path//path``); these segments are just ignored.
#         """
#         path = self.path_info
#         if not path:
#             return None
#         while path.startswith('/'):
#             self.script_name += '/'
#             path = path[1:]
#         if '/' not in path:
#             self.script_name += path
#             self.path_info = ''
#             return path
#         else:
#             segment, path = path.split('/', 1)
#             self.path_info = '/' + path
#             self.script_name += segment
#             return segment

#     def path_info_peek(self):
#         """
#         Returns the next segment on PATH_INFO, or None if there is no
#         next segment.  Doesn't modify the environment.
#         """
#         path = self.path_info
#         if not path:
#             return None
#         path = path.lstrip('/')
#         return path.split('/', 1)[0]

#     def _urlvars__get(self):
#         """
#         Return any *named* variables matched in the URL.

#         Takes values from ``environ['wsgiorg.routing_args']``.
#         Systems like ``routes`` set this value.
#         """
#         if 'paste.urlvars' in self.environ:
#             return self.environ['paste.urlvars']
#         elif 'wsgiorg.routing_args' in self.environ:
#             return self.environ['wsgiorg.routing_args'][1]
#         else:
#             result = {}
#             self.environ['wsgiorg.routing_args'] = ((), result)
#             return result

#     def _urlvars__set(self, value):
#         environ = self.environ
#         if 'wsgiorg.routing_args' in environ:
#             environ['wsgiorg.routing_args'] = (environ['wsgiorg.routing_args'][0], value)
#             if 'paste.urlvars' in environ:
#                 del environ['paste.urlvars']
#         elif 'paste.urlvars' in environ:
#             environ['paste.urlvars'] = value
#         else:
#             environ['wsgiorg.routing_args'] = ((), value)

#     def _urlvars__del(self):
#         if 'paste.urlvars' in self.environ:
#             del self.environ['paste.urlvars']
#         if 'wsgiorg.routing_args' in self.environ:
#             if not self.environ['wsgiorg.routing_args'][0]:
#                 del self.environ['wsgiorg.routing_args']
#             else:
#                 self.environ['wsgiorg.routing_args'] = (self.environ['wsgiorg.routing_args'][0], {})
            
#     urlvars = property(_urlvars__get, _urlvars__set, _urlvars__del, doc=_urlvars__get.__doc__)

#     def _urlargs__get(self):
#         """
#         Return any *positional* variables matched in the URL.

#         Takes values from ``environ['wsgiorg.routing_args']``.
#         Systems like ``routes`` set this value.
#         """
#         if 'wsgiorg.routing_args' in self.environ:
#             return self.environ['wsgiorg.routing_args'][0]
#         else:
#             # Since you can't update this value in-place, we don't need
#             # to set the key in the environment
#             return ()

#     def _urlargs__set(self, value):
#         environ = self.environ
#         if 'paste.urlvars' in environ:
#             # Some overlap between this and wsgiorg.routing_args; we need
#             # wsgiorg.routing_args to make this work
#             routing_args = (value, environ.pop('paste.urlvars'))
#         elif 'wsgiorg.routing_args' in environ:
#             routing_args = (value, environ['wsgiorg.routing_args'][1])
#         else:
#             routing_args = (value, {})
#         environ['wsgiorg.routing_args'] = routing_args

#     def _urlargs__del(self):
#         if 'wsgiorg.routing_args' in self.environ:
#             if not self.environ['wsgiorg.routing_args'][1]:
#                 del self.environ['wsgiorg.routing_args']
#             else:
#                 self.environ['wsgiorg.routing_args'] = ((), self.environ['wsgiorg.routing_args'][1])

#     urlargs = property(_urlargs__get, _urlargs__set, _urlargs__del, _urlargs__get.__doc__)

#     def is_xhr(self):
#         """Returns a boolean if X-Requested-With is present and ``XMLHttpRequest``

#         Note: this isn't set by every XMLHttpRequest request, it is
#         only set if you are using a Javascript library that sets it
#         (or you set the header yourself manually).  Currently
#         Prototype and jQuery are known to set this header."""
#         return self.environ.get('HTTP_X_REQUESTED_WITH', '') == 'XMLHttpRequest'
#     is_xhr = property(is_xhr, doc=is_xhr.__doc__)

#     def _host__get(self):
#         """Host name provided in HTTP_HOST, with fall-back to SERVER_NAME"""
#         if 'HTTP_HOST' in self.environ:
#             return self.environ['HTTP_HOST']
#         else:
#             return '%(SERVER_NAME)s:%(SERVER_PORT)s' % self.environ
#     def _host__set(self, value):
#         self.environ['HTTP_HOST'] = value
#     def _host__del(self):
#         if 'HTTP_HOST' in self.environ:
#             del self.environ['HTTP_HOST']
#     host = property(_host__get, _host__set, _host__del, doc=_host__get.__doc__)

#     def _body__get(self):
#         """
#         Return the content of the request body.
#         """
#         try:
#             length = int(self.environ.get('CONTENT_LENGTH', '0'))
#         except ValueError:
#             return ''
#         c = self.body_file.read(length)
#         tempfile_limit = self.request_body_tempfile_limit
#         if tempfile_limit and len(c) > tempfile_limit:
#             fileobj = tempfile.TemporaryFile()
#             fileobj.write(c)
#             fileobj.seek(0)
#         else:
#             fileobj = StringIO(c)
#         # We don't want/need to lose CONTENT_LENGTH here (as setting
#         # self.body_file would do):
#         self.environ['wsgi.input'] = fileobj
#         return c

#     def _body__set(self, value):
#         if value is None:
#             del self.body
#             return
#         if not isinstance(value, str):
#             raise TypeError(
#                 "You can only set Request.body to a str (not %r)" % type(value))
#         body_file = StringIO(value)
#         self.body_file = body_file
#         self.environ['CONTENT_LENGTH'] = str(len(value))

#     def _body__del(self, value):
#         del self.body_file

#     body = property(_body__get, _body__set, _body__del, doc=_body__get.__doc__)

#     def str_POST(self):
#         """
#         Return a MultiDict containing all the variables from a POST
#         form request.  Does *not* return anything for non-POST
#         requests or for non-form requests (returns empty dict-like
#         object in that case).
#         """
#         env = self.environ
#         if self.method != 'POST':
#             return NoVars('Not a POST request')
#         if 'webob._parsed_post_vars' in env:
#             vars, body_file = env['webob._parsed_post_vars']
#             if body_file is self.body_file:
#                 return vars
#         # Paste compatibility:
#         if 'paste.parsed_formvars' in env:
#             # from paste.request.parse_formvars
#             vars, body_file = env['paste.parsed_formvars']
#             if body_file is self.body_file:
#                 # FIXME: is it okay that this isn't *our* MultiDict?
#                 return vars
#         content_type = self.content_type
#         if ';' in content_type:
#             content_type = content_type.split(';', 1)[0]
#         if content_type not in ('', 'application/x-www-form-urlencoded',
#                                 'multipart/form-data'):
#             # Not an HTML form submission
#             return NoVars('Not an HTML form submission (Content-Type: %s)'
#                           % content_type)
#         if 'CONTENT_LENGTH' not in env:
#             # FieldStorage assumes a default CONTENT_LENGTH of -1, but a
#             # default of 0 is better:
#             env['CONTENT_TYPE'] = '0'
#         fs_environ = env.copy()
#         fs_environ['QUERY_STRING'] = ''
#         fs = cgi.FieldStorage(fp=self.body_file,
#                               environ=fs_environ,
#                               keep_blank_values=True)
#         vars = MultiDict.from_fieldstorage(fs)
#         FakeCGIBody.update_environ(env, vars)
#         env['webob._parsed_post_vars'] = (vars, self.body_file)
#         return vars

#     str_POST = property(str_POST, doc=str_POST.__doc__)

#     str_postvars = deprecated_property(str_POST, 'str_postvars',
#                                        'use str_POST instead')

#     def POST(self):
#         """
#         Like ``.str_POST``, but may decode values and keys
#         """
#         vars = self.str_POST
#         if self.charset:
#             vars = UnicodeMultiDict(vars, encoding=self.charset,
#                                     errors=self.unicode_errors,
#                                     decode_keys=self.decode_param_names)
#         return vars

#     POST = property(POST, doc=POST.__doc__)

#     postvars = deprecated_property(POST, 'postvars',
#                                    'use POST instead')

#     def str_GET(self):
#         """
#         Return a MultiDict containing all the variables from the
#         QUERY_STRING.
#         """
#         env = self.environ
#         source = env.get('QUERY_STRING', '')
#         if 'webob._parsed_query_vars' in env:
#             vars, qs = env['webob._parsed_query_vars']
#             if qs == source:
#                 return vars
#         if not source:
#             vars = MultiDict()
#         else:
#             vars = MultiDict(cgi.parse_qsl(
#                 source, keep_blank_values=True,
#                 strict_parsing=False))
#         env['webob._parsed_query_vars'] = (vars, source)
#         return vars

#     str_GET = property(str_GET, doc=str_GET.__doc__)

#     str_queryvars = deprecated_property(str_GET, 'str_queryvars',
#                                         'use str_GET instead')
                                        

#     def GET(self):
#         """
#         Like ``.str_GET``, but may decode values and keys
#         """
#         vars = self.str_GET
#         if self.charset:
#             vars = UnicodeMultiDict(vars, encoding=self.charset,
#                                     errors=self.unicode_errors,
#                                     decode_keys=self.decode_param_names)
#         return vars

#     GET = property(GET, doc=GET.__doc__)

#     queryvars = deprecated_property(GET, 'queryvars',
#                                     'use GET instead')

#     def str_params(self):
#         """
#         A dictionary-like object containing both the parameters from
#         the query string and request body.
#         """
#         return NestedMultiDict(self.str_GET, self.str_POST)

#     str_params = property(str_params, doc=str_params.__doc__)

#     def params(self):
#         """
#         Like ``.str_params``, but may decode values and keys
#         """
#         params = self.str_params
#         if self.charset:
#             params = UnicodeMultiDict(params, encoding=self.charset,
#                                       errors=self.unicode_errors,
#                                       decode_keys=self.decode_param_names)
#         return params

#     params = property(params, doc=params.__doc__)

#     def str_cookies(self):
#         """
#         Return a *plain* dictionary of cookies as found in the request.
#         """
#         env = self.environ
#         source = env.get('HTTP_COOKIE', '')
#         if 'webob._parsed_cookies' in env:
#             vars, var_source = env['webob._parsed_cookies']
#             if var_source == source:
#                 return vars
#         vars = {}
#         if source:
#             cookies = BaseCookie()
#             cookies.load(source)
#             for name in cookies:
#                 vars[name] = cookies[name].value
#         env['webob._parsed_cookies'] = (vars, source)
#         return vars

#     str_cookies = property(str_cookies, doc=str_cookies.__doc__)

#     def cookies(self):
#         """
#         Like ``.str_cookies``, but may decode values and keys
#         """
#         vars = self.str_cookies
#         if self.charset:
#             vars = UnicodeMultiDict(vars, encoding=self.charset,
#                                     errors=self.unicode_errors,
#                                     decode_keys=self.decode_param_names)
#         return vars

#     cookies = property(cookies, doc=cookies.__doc__)

#     def copy(self):
#         """
#         Copy the request and environment object.

#         This only does a shallow copy, except of wsgi.input
#         """
#         env = self.environ.copy()
#         data = self.body
#         tempfile_limit = self.request_body_tempfile_limit
#         if tempfile_limit and len(data) > tempfile_limit:
#             fileobj = tempfile.TemporaryFile()
#             fileobj.write(data)
#             fileobj.seek(0)
#         else:
#             fileobj = StringIO(data)
#         env['wsgi.input'] = fileobj
#         return self.__class__(env)

#     def copy_get(self):
#         """
#         Copies the request and environment object, but turning this request
#         into a GET along the way.  If this was a POST request (or any other verb)
#         then it becomes GET, and the request body is thrown away.
#         """
#         env = self.environ.copy()
#         env['wsgi.input'] = StringIO('')
#         env['CONTENT_LENGTH'] = '0'
#         if 'CONTENT_TYPE' in env:
#             del env['CONTENT_TYPE']
#         env['REQUEST_METHOD'] = 'GET'
#         return self.__class__(env)

#     def remove_conditional_headers(self, remove_encoding=True):
#         """
#         Remove headers that make the request conditional.

#         These headers can cause the response to be 304 Not Modified,
#         which in some cases you may not want to be possible.

#         This does not remove headers like If-Match, which are used for
#         conflict detection.
#         """
#         for key in ['HTTP_IF_MATCH', 'HTTP_IF_MODIFIED_SINCE',
#                     'HTTP_IF_RANGE', 'HTTP_RANGE']:
#             if key in self.environ:
#                 del self.environ[key]
#         if remove_encoding:
#             if 'HTTP_ACCEPT_ENCODING' in self.environ:
#                 del self.environ['HTTP_ACCEPT_ENCODING']

#     accept = converter(
#         environ_getter('HTTP_ACCEPT', rfc_section='14.1'),
#         _parse_accept, _serialize_accept, 'MIME Accept',
#         converter_args=('Accept', MIMEAccept, MIMENilAccept))

#     accept_charset = converter(
#         environ_getter('HTTP_ACCEPT_CHARSET', rfc_section='14.2'),
#         _parse_accept, _serialize_accept, 'accept header',
#         converter_args=('Accept-Charset', Accept, NilAccept))

#     accept_encoding = converter(
#         environ_getter('HTTP_ACCEPT_ENCODING', rfc_section='14.3'),
#         _parse_accept, _serialize_accept, 'accept header',
#         converter_args=('Accept-Encoding', Accept, NoAccept))

#     accept_language = converter(
#         environ_getter('HTTP_ACCEPT_LANGUAGE', rfc_section='14.4'),
#         _parse_accept, _serialize_accept, 'accept header',
#         converter_args=('Accept-Language', Accept, NilAccept))

#     ## FIXME: 14.8 Authorization
#     ## http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.8

#     def _cache_control__get(self):
#         """
#         Get/set/modify the Cache-Control header (section `14.9
#         <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.9>`_)
#         """
#         env = self.environ
#         value = env.get('HTTP_CACHE_CONTROL', '')
#         cache_header, cache_obj = env.get('webob._cache_control', (None, None))
#         if cache_obj is not None and cache_header == value:
#             return cache_obj
#         cache_obj = CacheControl.parse(value, type='request')
#         env['webob._cache_control'] = (value, cache_obj)
#         return cache_obj

#     def _cache_control__set(self, value):
#         env = self.environ
#         if not value:
#             value = ""
#         if isinstance(value, dict):
#             value = CacheControl(value, type='request')
#         elif isinstance(value, CacheControl):
#             str_value = str(value)
#             env['HTTP_CACHE_CONTROL'] = str_value
#             env['webob._cache_control'] = (str_value, value)
#         else:
#             env['HTTP_CACHE_CONTROL'] = str(value)
#             if 'webob._cache_control' in env:
#                 del env['webob._cache_control']

#     def _cache_control__del(self, value):
#         env = self.environ
#         if 'HTTP_CACHE_CONTROL' in env:
#             del env['HTTP_CACHE_CONTROL']
#         if 'webob._cache_control' in env:
#             del env['webob._cache_control']

#     cache_control = property(_cache_control__get, _cache_control__set, _cache_control__del, doc=_cache_control__get.__doc__)

#     date = converter(
#         environ_getter('HTTP_DATE', rfc_section='14.8'),
#         _parse_date, _serialize_date, 'HTTP date')

#     if_match = converter(
#         environ_getter('HTTP_IF_MATCH', rfc_section='14.24'),
#         _parse_etag, _serialize_etag, 'ETag', converter_args=(True,))

#     if_modified_since = converter(
#         environ_getter('HTTP_IF_MODIFIED_SINCE', rfc_section='14.25'),
#         _parse_date, _serialize_date, 'HTTP date')

#     if_none_match = converter(
#         environ_getter('HTTP_IF_NONE_MATCH', rfc_section='14.26'),
#         _parse_etag, _serialize_etag, 'ETag', converter_args=(False,))

#     if_range = converter(
#         environ_getter('HTTP_IF_RANGE', rfc_section='14.27'),
#         _parse_if_range, _serialize_if_range, 'IfRange object')

#     if_unmodified_since = converter(
#         environ_getter('HTTP_IF_UNMODIFIED_SINCE', rfc_section='14.28'),
#         _parse_date, _serialize_date, 'HTTP date')

#     max_forwards = converter(
#         environ_getter('HTTP_MAX_FORWARDS', rfc_section='14.31'),
#         _parse_int, _serialize_int, 'int')

#     pragma = environ_getter('HTTP_PRAGMA', rfc_section='14.32')

#     range = converter(
#         environ_getter('HTTP_RANGE', rfc_section='14.35'),
#         _parse_range, _serialize_range, 'Range object')

#     referer = environ_getter('HTTP_REFERER', rfc_section='14.36')
#     referrer = referer

#     user_agent = environ_getter('HTTP_USER_AGENT', rfc_section='14.43')

#     def __repr__(self):
#         msg = '<%s at %x %s %s>' % (
#             self.__class__.__name__,
#             abs(id(self)), self.method, self.url)
#         return msg

#     def __str__(self):
#         url = self.url
#         host = self.host_url
#         assert url.startswith(host)
#         url = url[len(host):]
#         if 'Host' not in self.headers:
#             self.headers['Host'] = self.host
#         parts = ['%s %s' % (self.method, url)]
#         for name, value in sorted(self.headers.items()):
#             parts.append('%s: %s' % (name, value))
#         parts.append('')
#         parts.append(self.body)
#         return '\r\n'.join(parts)

#     def call_application(self, application, catch_exc_info=False):
#         """
#         Call the given WSGI application, returning ``(status_string,
#         headerlist, app_iter)``

#         Be sure to call ``app_iter.close()`` if it's there.

#         If catch_exc_info is true, then returns ``(status_string,
#         headerlist, app_iter, exc_info)``, where the fourth item may
#         be None, but won't be if there was an exception.  If you don't
#         do this and there was an exception, the exception will be
#         raised directly.
#         """
#         captured = []
#         output = []
#         def start_response(status, headers, exc_info=None):
#             if exc_info is not None and not catch_exc_info:
#                 raise exc_info[0], exc_info[1], exc_info[2]
#             captured[:] = [status, headers, exc_info]
#             return output.append
#         app_iter = application(self.environ, start_response)
#         if (not captured
#             or output):
#             try:
#                 output.extend(app_iter)
#             finally:
#                 if hasattr(app_iter, 'close'):
#                     app_iter.close()
#             app_iter = output
#         if catch_exc_info:
#             return (captured[0], captured[1], app_iter, captured[2])
#         else:
#             return (captured[0], captured[1], app_iter)

#     # Will be filled in later:
#     ResponseClass = None

#     def get_response(self, application, catch_exc_info=False):
#         """
#         Like ``.call_application(application)``, except returns a
#         response object with ``.status``, ``.headers``, and ``.body``
#         attributes.

#         This will use ``self.ResponseClass`` to figure out the class
#         of the response object to return.
#         """
#         if catch_exc_info:
#             status, headers, app_iter, exc_info = self.call_application(
#                 application, catch_exc_info=True)
#             del exc_info
#         else:
#             status, headers, app_iter = self.call_application(
#                 application, catch_exc_info=False)
#         return self.ResponseClass(
#             status=status, headerlist=headers, app_iter=app_iter,
#             request=self)

#     #@classmethod
#     def blank(cls, path, environ=None, base_url=None, headers=None):
#         """
#         Create a blank request environ (and Request wrapper) with the
#         given path (path should be urlencoded), and any keys from
#         environ.

#         The path will become path_info, with any query string split
#         off and used.

#         All necessary keys will be added to the environ, but the
#         values you pass in will take precedence.  If you pass in
#         base_url then wsgi.url_scheme, HTTP_HOST, and SCRIPT_NAME will
#         be filled in from that value.
#         """
#         if _SCHEME_RE.search(path):
#             scheme, netloc, path, qs, fragment = urlparse.urlsplit(path)
#             if fragment:
#                 raise TypeError(
#                     "Path cannot contain a fragment (%r)" % fragment)
#             if qs:
#                 path += '?' + qs
#             if ':' not in netloc:
#                 if scheme == 'http':
#                     netloc += ':80'
#                 elif scheme == 'https':
#                     netloc += ':443'
#                 else:
#                     raise TypeError("Unknown scheme: %r" % scheme)
#         else:
#             scheme = 'http'
#             netloc = 'localhost:80'
#         if path and '?' in path:
#             path_info, query_string = path.split('?', 1)
#             path_info = urllib.unquote(path_info)
#         else:
#             path_info = urllib.unquote(path)
#             query_string = ''
#         env = {
#             'REQUEST_METHOD': 'GET',
#             'SCRIPT_NAME': '',
#             'PATH_INFO': path_info or '',
#             'QUERY_STRING': query_string,
#             'SERVER_NAME': netloc.split(':')[0],
#             'SERVER_PORT': netloc.split(':')[1],
#             'HTTP_HOST': netloc,
#             'SERVER_PROTOCOL': 'HTTP/1.0',
#             'wsgi.version': (1, 0),
#             'wsgi.url_scheme': scheme,
#             'wsgi.input': StringIO(''),
#             'wsgi.errors': sys.stderr,
#             'wsgi.multithread': False,
#             'wsgi.multiprocess': False,
#             'wsgi.run_once': False,
#             }
#         if base_url:
#             scheme, netloc, path, query, fragment = urlparse.urlsplit(base_url)
#             if query or fragment:
#                 raise ValueError(
#                     "base_url (%r) cannot have a query or fragment"
#                     % base_url)
#             if scheme:
#                 env['wsgi.url_scheme'] = scheme
#             if netloc:
#                 if ':' not in netloc:
#                     if scheme == 'http':
#                         netloc += ':80'
#                     elif scheme == 'https':
#                         netloc += ':443'
#                     else:
#                         raise ValueError(
#                             "Unknown scheme: %r" % scheme)
#                 host, port = netloc.split(':', 1)
#                 env['SERVER_PORT'] = port
#                 env['SERVER_NAME'] = host
#                 env['HTTP_HOST'] = netloc
#             if path:
#                 env['SCRIPT_NAME'] = urllib.unquote(path)
#         if environ:
#             env.update(environ)
#         obj = cls(env)
#         if headers is not None:
#             obj.headers.update(headers)
#         return obj

#     blank = classmethod(blank)

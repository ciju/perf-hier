import cgi, os, urllib2, datetime, re, itertools

from plogging import log

import logging
logging.getLogger().setLevel(logging.DEBUG)

logging.warn('app recycling:' + str(datetime.datetime.now()))

from utils import slashify

from django.utils import simplejson as json

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.db import polymodel, Key

import fork_join_queue

# from models import EventTypes,
from models import Event, Dimentions, Project, AccntAuthorization, AggregateCounterDict, Aggregate, Timeline
from decorators import authorized_role, returns_json, authorized_role_new, work_queue_only, allowed_for

__author__= "ciju.ch3rian@gmail.com (ciju cherian)"

APP_ROOT = os.path.normpath(os.path.dirname(__file__))

LOCAL = os.environ["SERVER_SOFTWARE"].startswith("Development")
APP_ID = os.environ["APPLICATION_ID"]
VER_ID = os.environ['CURRENT_VERSION_ID']

# todo: give this a better name!
class Data(db.Model):
    # time = db.DateTimeProperty(auto_now=True)
    data = db.TextProperty()
    work_index = db.IntegerProperty()

class ComputeAndLogStats(webapp.RequestHandler):

    FJ_Queue = fork_join_queue.ShardedForkJoinQueue(
        Data,
        Data.work_index,
        '/work/flipjoin_queue', # the url
        'fjqueue',              # queue name
        batch_size=100,         # may be this could be time based.
        batch_period_ms=1000,
        lock_timeout_ms=10000,
        sync_timeout_ms=250,
        stall_timeout_ms=30000,
        acquire_timeout_ms=10,
        acquire_attempts=50,
        shard_count=1)


    @classmethod
    def __entry_list(self, data, tab_prefix=""):
        """ take the hierarchical data supplied by client and
        make a list of tuple of its name and val
        """
        if tab_prefix == '':
            new_prefix = data['name']
        else:
            new_prefix = tab_prefix + '/' + data['name']

        arr = [ (new_prefix, data['val']) ]
        for c in data['childrens']:
            arr += self.__entry_list(c, new_prefix)
        return arr

    @classmethod
    def enqueue(cls, req):
        """Call it to get all the needed params from the logging request.
        """
        widx = cls.FJ_Queue.next_index()
        logging.info(Dimentions.get_stats(req))
        Data(data       = json.dumps(Dimentions.get_stats(req)),
             work_index = widx).put()
        cls.FJ_Queue.add(widx)
        return

    @classmethod
    def calc_req_tag_val(cls, req):
        "(dimention, (tag,value)) pairs"
        ph_id = req.get('ph_id')
        log(json.loads(req.get('data')))
        entries = cls.__entry_list( json.loads(req.get('data')) )
        cats = Dimentions.get_dim_and_met(req, req.get('time'))

        result = {'aggregate': {}, 'timeline': {}}
        for i in ['aggregate', 'timeline']:
            res = result[i]
            stat = cats[i]
            for c in stat:
                typ = slashify(ph_id, c[0])
                if typ in res:
                    logging.error(' the string should be unique for a single request:' + typ)
                res[typ] = { c[1] : entries }

        return result

    @work_queue_only
    def post(self):
        cls = self.__class__
        stats = {}
        # todo: define this limit properly.
        work_list = cls.FJ_Queue.pop_request(self.request)
        logging.info('work list len: ' + str(len(work_list)))

        def calc_stat(acc, tvs):
            for tv in tvs:
                k = tv[0]
                if k not in acc:
                    acc[k] = (0, 0)

                c, v = acc[k]
                acc[k] = (c+1, v+tv[1])

            return

        def accumulate(acc, cnts):
            for i in ['aggregate', 'timeline']:
                if i not in acc:
                    acc[i] = {}

                for j in cnts[i]:
                    if j not in acc[i]:
                        acc[i][j] = {}
                    for k in cnts[i][j]:
                        if k not in acc[i][j]:
                            acc[i][j][k] = {}
                        calc_stat(acc[i][j][k], cnts[i][j][k])


        # todo: calculate the stats first. and then read and udpate the current
        # values.
        for w in work_list:
            d = json.loads(str(w.data))
            i = int(d['ph_id'])
            if i not in stats:
                stats[i] = {}

            logging.info(cls.calc_req_tag_val(d))
            accumulate(stats[i], cls.calc_req_tag_val(d))

        # delete the work, because otherwise it eats on datastore quota.
        db.delete(work_list)

        logging.info('stats ')
        logging.info(stats)
        AggregateCounterDict.update_with_stats(stats)
        return



# note: what about proxy caching. what about cookies being cached by proxy.

class ApiRegisterEvent(webapp.RequestHandler):

    def get(self):
        ComputeAndLogStats.enqueue(self.request)

        self.response.headers["Content-Type"] = "text/javascript; charset=UTF-8"
        self.response.set_status(204)
        return


class UserInfo(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        admin = users.is_current_user_admin()


class Login(webapp.RequestHandler):
    def get(self):
        url = self.request.get("continue")
        self.redirect(users.create_login_url(url))

class Logout(webapp.RequestHandler):
    def get(self):
        url = self.request.get("continue")
        self.redirect(users.create_logout_url(url))


# http://code.google.com/p/google-app-engine-samples/source/browse/trunk/myhangouts/myhangouts.py
# This handler allows the functions defined in the RPCHandler class to
# be called automatically by remote code.
# modified by - ciju
class RPCHandler(webapp.RequestHandler):
    def _get_fn_doc_hash(self, f, s, fname):
        return {'fun': fname, 'doc':getattr(RPCHandler, s+f).__doc__}

    def _methods_starting_with(self, s):
        ms = [re.search('^'+s+'(.*)', m) for m in
              dir(RPCHandler)]
        return [r.group(1) for r in filter(None, ms)]

    def _gen_doc(self, typ):
        bfix = typ+'_'
        pfix = 'rpc_'+bfix
        return [self._get_fn_doc_hash(f, pfix, bfix+f) for f in
                self._methods_starting_with(pfix)]

    @returns_json
    def _process_request(self, suffix='rpc_'):
        args = {}
        for arg in self.request.arguments():
            args[str(arg)] = str(self.request.get(arg))

        action, resource = None, None
        if 'action' in args:
            action = args['action']
            del args['action']
        if 'ph_id' in args:
            resource = args['ph_id']
            del args['ph_id']

        func = getattr(self, suffix + action, None)
        if not func:
            res = { 'status': 'not_found' }
        elif resource:
            res = func(resource, **args)
        else:
            res = func(**args)

        if 'status' not in res:
            res = { 'status': 'ok', 'result': res }

        { 'not_found' : lambda: self.error(404)
          , 'error'     : lambda: self.error(500)
          }.get(res['status'], lambda: 'do nothing')()

        return res

    def get(self):
        return self._process_request()

    def post(self):
        return self._process_request()


    def rpc_get_list_rpc_methods(self):
        methods = dict([[m+'s', self._gen_doc(m)] for m in
                        ['get', 'post']])
        return { 'methods' : methods }


    # * session related *
    def rpc_create_login_url(self):
        return { 'login_url': users.create_login_url("/") }

    @allowed_for('user')
    def rpc_create_logout_url(self):
        return { 'logout_url': users.create_logout_url("/") }

    def rpc_get_user_info(self):
        user      = users.get_current_user()
        logged_in = True if user else False
        is_admin  = users.is_current_user_admin()


        res = { 'logged_in' : logged_in }
        if logged_in:
            res['nick']  = user.nickname()
            res['email'] = user.email()
        if is_admin:
            res['admin'] = True
        if LOCAL:
            res['dev'] = True
        return res


    # * project management *
    @allowed_for('user')
    def rpc_post_create_project(self, project, description=""):
        p = Project.create(self.user, project, description)
        if p:
            res = {'id': p.ph_id, 'name': p.name}
        else:
            res = {'status': 'error', 'message': 'couldnt create the project'}
        return res

    @allowed_for('user')
    def rpc_get_list_of_projects(self):
        return [{'project':p.ph_id, 'name':p.name, 'desc':p.desc}
                for p in Project.get_by_user(self.user)]

    @allowed_for('admin, author', 'project@Project')
    def rpc_get_project_details(self, project):
        return {'ph_id': project.ph_id, 'name': project.name}

    @allowed_for('admin, author', 'name@Project')
    def rpc_get_project_by_name(self, name):
        return {'project':name.ph_id, 'name': name.name}



    # project stat details
    @allowed_for('admin, author, view', 'project@Project')
    def rpc_get_meta_dimentions(self, project):
        return Dimentions.meta_dimentions

    @allowed_for('admin, author, view', 'project@Project')
    def rpc_get_metric_tags(self, project):
        """Hash of dimentions and there metrics.
        """
        if not project:
            return {'status': 'error', 'message': 'project doesnt exist'}
        return Aggregate.get_dimentions(project.ph_id)

    @allowed_for('admin, author', 'project@Project')
    def rpc_post_authorize(self, project, useremail=None, typ='view'):
        AccntAuthorization.authorize(project, useremail, typ)
        return {}

    @allowed_for('admin, author, view', 'project@Project')
    def rpc_get_aggregate_metrics(self, project, typ='general/aggregate'):
        d,m = typ.split('/')
        res = Aggregate.get_aggregate(project.ph_id, slashify(project.ph_id, 'aggregate', d))
        return res[m]

    @allowed_for('admin, author, view', 'project@Project')
    def rpc_get_csv_timelines(self, project, typ='general/aggregate', tag=None):
        return Timeline.get_timeline(project.ph_id, slashify(project.ph_id, 'timeline', typ), tag)


class MainPage(webapp.RequestHandler):
    def get(self):
        f = 'index.html'

        if not LOCAL and not self.request.get('dbg') == 'true':
            f = os.path.join('build', f)

        path = os.path.join(os.path.dirname(__file__), f)
        # self.response.headers["Cache-Control"] = "private; max-age=3153600"
        # template_values['events'][1]['time'] = int(time.time()*1000)
        self.response.out.write(open(path, 'r').read().replace('REPLACE_WITH_APP_STATE', '"dev"'))

class AggregateHourlyStats(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        admin = users.is_current_user_admin()

        AggregateCounterDict.aggregate_stats(LOCAL)

        return {}


application = webapp.WSGIApplication(
    [
        ('/', MainPage),
        ('/login', Login),
        ('/logout', Logout),
        # not api, but ajax functions
        ('/api/register_event*', ApiRegisterEvent),
        ('/work/flipjoin_queue', ComputeAndLogStats),
        ('/task/aggregate_hourly_stats', AggregateHourlyStats),
        ('/rpc', RPCHandler)
        ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

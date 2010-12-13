import os
import re
import time
import datetime
import urllib2
import itertools

import logging

from django.utils import simplejson as json

from plogging import log
from utils import slashify, dashify
from google.appengine.api import users
from google.appengine.ext import db
from decorators import transaction
from decorators import prefix_func_name

import utils

__author__ = "ciju.ch3rian@gmail.com (ciju cherian)"

PROJECT_LIMIT = 20

class Project(db.Model):

    name = db.StringProperty(indexed=True, required=True)
    # ph_id = db.IntegerProperty(indexed=True, required=True)
    desc       = db.StringProperty(indexed=False, required=False)
    last_hr    = db.DateTimeProperty(required=False, indexed=False) # last time actual stats were updated.
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)

    @classmethod
    def create(cls, user, proj, desc):
        # put a limit on number of projects from a user.
        if Project.all().count() > PROJECT_LIMIT:
            logging.warn('Project limit reached')
            return False

        # check if project with same name already exists.
        if Project.all().filter('name = ', proj).fetch(limit=1):
            return False

        p = Project(name=proj, desc=desc)
        p.put()
        AccntAuthorization(author=user, project=p,
                           authorization='author').put()
        return p

    @classmethod
    def get_by_user(cls, user):
        acnts = AccntAuthorization.gql('where author = :u ', u=user)
        return [a.project for a in acnts]

    @classmethod
    def get_by_name(cls, user, name):
        return Project.gql('where name = :n', n=name).fetch(1)[0]

    @classmethod
    def get_by_project(cls, ph_id):
        return Project.get_by_id(int(ph_id))

    def check_access(self, user, types):
        q = AccntAuthorization.gql(
            'where project = :p and author = :u and authorization in :a',
            p=self, a=types, u=user)

        log(types, q.count())
        return AccntAuthorization.gql(
            'where project = :p and author = :u and authorization in :a ',
            p=self, a=types, u=user).count() > 0

    @property
    def ph_id(self):
        return int(self.key().id())

# an anon user. whos key is used in AccntAuthorization to figure
# out the permissions.

class AccntAuthorization(db.Model):
    """Associates a PerfHierAccnt to a Project. The reference for
    PerfHierAccnt could be None. The None once are used to
    represent authorizations to anonymous (not logged in) users.
    """
    auth_types = ('full', 'view', 'author', 'edit')

    # for anon user authorization author should be 'None'
    author = db.UserProperty(indexed=True)
    project = db.ReferenceProperty(Project,
                                   collection_name='user_authorizations',
                                   required=True)
    authorization = db.StringProperty(choices=auth_types)

    @classmethod
    def authorize(cls, project, user, typ='view'):
        if user:
            author = users.User(user)
        else:
            author = None

        AccntAuthorization(author=author, project=project,
                           authorization=typ).put()

        return True



# invarients:
# - once paid is made, it wont change. its the handle to stats to
#   be measured by the user.
# - paid could be the key().id() for the PAA instance.

class BaseModel(db.Model):
    @classmethod
    @transaction
    def update_or_insert(cls, key_name, **kwds):
        e = cls.get_by_key_name(key_name, parent=kwds.get('parent'))
        if e is None:
            e = cls(key_name=key_name, **kwds)
        else:
            prop = cls.properties().keys()
            for k in kwds.keys():
                if k in prop: setattr(e, k, kwds[k])
        e.put()
        return e

    @classmethod
    def filter_prefix(cls, property_name, prefix):
        query = cls.all()
        query.filter("%s >= " % property_name, u"%s" % prefix)
        query.filter("%s < " % property_name, u"%s\xEF\xBF\xBD" % prefix)
        return query

    @classmethod
    def filter_key_prefix(cls, prefix, keys_only=False):
        query = cls.all(keys_only=keys_only)
        query.filter("__key__ >= ", db.Key.from_path(cls.__name__, prefix))
        query.filter("__key__ < ", db.Key.from_path(cls.__name__, prefix + u"\xEF\xBF\xBD"))
        return query


class Event(BaseModel):
    etype = db.StringProperty(required=True)
    browser_type = db.StringProperty()
    request_time = db.IntegerProperty()
    # request_time = db.DateTimeProperty()
    remote_ip = db.StringProperty()
    # geo = db.GeoPtProperty()


class Stat(BaseModel):
    val = db.IntegerProperty(indexed=False, default=0)
    stat = db.TextProperty(indexed=False, default='{}', required=True)

    @classmethod
    def get_key(cls, k):
        return 'stat:'

    @classmethod
    def filter_int_keys_with_prefix(cls, prefix):
        query = cls.all()
        prefix = cls.get_key(prefix)
        query.filter("__key__ >= ",
                     db.Key.from_path(cls.__name__, prefix+'0'))
        query.filter("__key__ <= ",
                     db.Key.from_path(cls.__name__, prefix+'9'))
        return query

    @classmethod
    def keys_with_prefix(cls, prefix):
        query = cls.all()
        # prefix = cls.get_key(prefix)
        query.filter("__key__ >= ",
                     db.Key.from_path(cls.__name__, prefix))
        query.filter("__key__ < ",
                     db.Key.from_path(cls.__name__, prefix +
                                      u"\xEF\xBF\xBD"))
        return query

    @classmethod
    def get_all(cls, keys):
        p = cls.get_key('')
        return cls.get_by_key_name([p+k for k in keys])


    @classmethod
    def update_keys(cls, cnts):
        keys = cnts.keys()
        objs = cls.get_all(keys)

        for i, k in enumerate(keys):
            if objs[i]:
                objs[i].val += cnts[k]
            else:
                objs[i] = cls(key_name=cls.get_key(k), val=cnts[k])

        db.put(objs)
        return

    @classmethod
    @transaction
    def add(cls, k, val):
        key = cls.get_key( k )
        c = cls.get_by_key_name( key )
        if c is None:
            c = cls(key_name=key, val=0)

        c.val += val
        c.put()

    @classmethod
    def get_val(cls, k):
        c = cls.get_by_key_name( cls.get_key( k ))
        if c is None:
            return 0
        else:
            return c.val


    # new fns, for aggregate and timeline
    # @classmethod
    # def get_obj(cls, proj, typ):
    #     k = cls.get_key(proj, typ)
    #     return cls.get_by_key_name(k)

    @classmethod
    def create_obj(cls, proj, typ, stat="{}"):
        k = cls.get_key(proj, typ)
        return cls(key_name=k, stat=stat)

    @classmethod
    def get_or_create_obj(cls, proj, typ):
        obj = cls.get_obj(proj, typ)
        if not obj:
            obj = cls.create_obj(proj, typ)
        return obj

    @classmethod
    @transaction
    def update_and_save(cls, proj, typ, stat, updt_fn):
        obj = cls.get_or_create_obj(proj, typ)
        obj.stat = json.dumps(updt_fn(stat, json.loads(obj.stat)))
        obj.put()

    @classmethod
    def get_obj(cls, proj, typ):
        # log( cls.get_key( proj, typ) )
        return cls.get_by_key_name( cls.get_key(proj, typ) )

    # @classmethod
    # def get_metrics(cls, proj, typ):
    #     obj = cls.get_by_key_name( cls.get_key(proj, typ) )
    #     return [i for i in obj.stat]

    @classmethod
    def get_dimentions(cls, proj):
        h = {}
        for i in cls.keys_with_prefix(cls.get_key(proj, slashify(proj))):
            d = i.key().name().split('/')[-1]
            h[d] = [j for j in json.loads(i.stat)]

        return h



class Aggregate(Stat):
    @classmethod
    def get_key(cls, proj, typ):
        return 'stat:aggregate:'+ slashify( str(proj), typ)

    @classmethod
    def save_aggregate(cls, proj, typ, stat):
        def updt_fn(stat, cnts):
            for dimp in stat:
                for dims in stat[dimp]:
                    if dimp not in cnts:
                        cnts[dimp] = {}
                    if dims not in cnts[dimp]:
                        cnts[dimp][dims] = [0,0]

                    cnts[dimp][dims][0] += stat[dimp][dims][0]
                    cnts[dimp][dims][1] += stat[dimp][dims][1]

            return cnts

        cls.update_and_save(proj, typ, stat, updt_fn)

    @classmethod
    def get_aggregate(cls, proj, typ):
        obj = cls.get_obj(proj, typ)
        if not obj:
            return None

        return json.loads(obj.stat)


class Timeline(Stat):
    @classmethod
    def get_key(cls, proj, typ):
        return 'stat:timeline:'+slashify( str(proj), typ)

    @classmethod
    def save_timeline(cls, proj, typ, stat):

        # todo: this has to be kept with logic which divides the tags into
        # prefix and sufix (example month prefix tag).

        def idx2ts(i, ms):
            return utils.add_hrs(i, ms)

        def ts2idx(t, ms):          # monthly assumption.
            return utils.timedelta_total_hours( t - ms )

        def updt_cnts(orig, updt, ts, ms):
            l = len(orig)
            i = ts2idx(ts, ms)

            if i < l:
                orig[i][1][0] += updt[0]
                orig[i][1][1] += updt[1]
            else:
                for j in range(i-l):
                    orig.append( (str(idx2ts(l+j, ms)), (0, 0)) )
                else:
                    orig.append( (str(ts), updt) )

        def updt_fn(stat, cnts):
            for dimp in stat:
                ts = utils.str2ts(dimp)
                ms = utils.month_start(now=ts)

                for dims in stat[dimp]:
                    if dims not in cnts:
                        cnts[dims] = []
                    updt_cnts(cnts[dims], stat[dimp][dims], ts, ms)

            # get the time stamp.
            # for each of the tags, append the time stamp with the cnt and value.

            # todo: stat has the timestamp and corresponding [cnt, val] for the
            # stats to be updated. find out the corresponding place and update
            # them if they exist. else create the place in timeline without any
            # gap.

            # calculate the index from the timestamp.
            return cnts

        cls.update_and_save(proj, typ, stat, updt_fn)

    @classmethod
    def get_timeline(cls, proj, typ, tag=None):
        # todo: the fuck, how could u hard code these things.
        prv_obj = cls.get_obj(proj, utils.slashify(typ, 'hour_by_month', utils.month_tag(utils.last_month())))
        obj = cls.get_obj(proj, utils.slashify(typ, 'hour_by_month', utils.month_tag()) )

        def fill_entries(lst, ms, hrs):
            if len(lst) < last_month_hrs:
                lst.extend([str(utils.add_hrs(j, ms)), [0,0]] for j in range(len(lst), last_month_hrs))
            return lst

        last_month_hrs = utils.last_month().day*24
        ms = utils.month_start(now=utils.last_month())

        def normalize(res, ms, last_month_hrs):
            for i in res:
                res[i] = fill_entries(res[i], ms, last_month_hrs)
            return res


        if not prv_obj and not obj:
            return {}

        if prv_obj:
            res = normalize(json.loads(prv_obj.stat), ms, last_month_hrs)

        if obj:
            nres = json.loads(obj.stat)
            if not prv_obj:
                res = nres
            else:
                for t in nres:
                    if not t in res:
                        res[t] = fill_entries([], ms, last_month_hrs)
                    res[t].extend(nres[t])

        if tag:
            return res[tag]

        return res


# todo: move to utils?
def flatten(lst):
    return list(itertools.chain(*lst))


# todo: how do we organize dimentions, meta-dimentions, and
# metrics. We need to get the timeline with a perticular metric
# ex: Firefox in browser dimention. Combination of dimentions ex:
# Firefox + a particular url, could be future feature. requires
# sampling.
class Dimentions:
    # todo: We need to get the list of metrics
    # automatically. What about urls, do we add them also into
    # the dimentions. We can, I guess there is it doesnt hurt
    # performance to add that.

    # todo: prefix_func_name should add fucntion name with '/' to the
    # return value. and also add those prefixes into the
    # dimentions list for class.

    # meta_dimentions = ['day', 'month', 'year', 'hour']
    meta_dimentions = ['hour']

    # note: any function which is not a dimention, should have
    # 'get_' or '__' as prefix.
    @classmethod
    def get_class_methods_not_starting_with_get(cls):
        s = '^(get_|__)(.*)'
        return [m for m in dir(cls) if (not re.search(s, m)) and callable(getattr(cls, m))]

    @classmethod
    def get_meta_dimentions(cls, time):
        """Returns tupes of meta dimentions. ex: (prefix_meta, suffix_meta)
        """
        def zerofy(i):
            if i < 10:
                return '0'+str(i)
            else:
                return str(i)

        y = str(time.year)
        m, d, h = map(zerofy, [time.month, time.day, time.hour])

        meta = [
            # ('year', dashify(y)),
            # ('month', dashify(y, m)),
            # ('day', dashify(y, m, d)),
            ('hour_by_month/'+str(dashify(y, m)), dashify(y, m, d, h))
            ]
        # log('meta : '+str(meta))
        return meta

    @classmethod
    def get_non_meta_dimentions(cls):
        return cls.get_class_methods_not_starting_with_get()

    @classmethod
    def get_dimentions(cls):
        d = cls.get_non_meta_dimentions()
        m = cls.meta_dimentions
        return [slashify(i) for i in d] + [slashify(i, j) for i in d for j in m]

    @classmethod
    def get_non_meta_dimentions_and_metrics(cls, req):
        """
        Parses the class functions and uses them to get the list
        of dimentions. For each dimentions it then calls the
        respective functions to get the corresponding metrics.
        """
        # res =
        # log(' ******** dimentions and metrics:   ', json.dumps(res, indent=2))
        # log(' ***** flatten:  ', json.dumps(flatten(res), indent=2))
        ms = cls.get_class_methods_not_starting_with_get()
        return [(i, getattr(cls, i)(req)) for i in ms]

    @classmethod
    def get_dim_and_met(cls, req, time):
        d = cls.get_non_meta_dimentions_and_metrics(req)
        m = cls.get_meta_dimentions(datetime.datetime.fromtimestamp(time))

        default = [(slashify('aggregate', i[0]), i[1]) for i in d]
        meta = [(slashify('timeline', i[0], i[1], j[0]), j[1]) for i in d for j in m]

        return { 'aggregate' : default, 'timeline' : meta }


    @classmethod
    def get_stats(cls, req):
        res = {
            'time'  : int(req.get('t') or time.time()),
            'ph_id' : req.get('ph_id'),
            'bt'    : req.get('bt'),
            # 'url'   : req.path,
            'data'  : req.get('data')
            }
        # res['time'] = req.get('t') or

        return res

    # dimentions defined as functions, which return the
    # dimention+metrics on being called
    @classmethod
    # @prefix_func_name
    def general(cls, req):
        return 'aggregate'

    @classmethod
    # @prefix_func_name
    def browser(cls, req):
        return req.get('bt').replace(':', '-')


    # @classmethod
    # # @prefix_func_name
    # def urls(cls, req):
    #     # todo: get the url and replace the site name etc.
    #     # return [req.get('url')]
    #     return urllib2.quote(req.get('url'), '')



    # todo: move all the functions dealing with hierarchy to one
    # class. ex: the TypeStrins methods, could be moved to this
    # file. CategorizedRequest needs the web request, rather than
    # having it as subclass of webapp.RequestHandler, just pass
    # it the request object. the metrics dont need the
    # request. the dimentions need it. even meta metrics r
    # defined in the app. So only dimentions need to be concerned
    # with request.

class AggregateCounterDict(db.Model):
    """Keeps a dict of counter entries and there aggregates in datastore. Also
    provides methods to update/add counters. The entries belong to a single
    project. And the whole dict is stored, as a json object.
    """
    project         = db.ReferenceProperty(Project, required=True)
    hr              = db.DateTimeProperty(auto_now=True)
    count_dict_dump = db.TextProperty()

    @classmethod
    def get_or_create_count_obj(cls, ph_id):
        project  = db.Key.from_path('Project', int(ph_id))
        now      = datetime.datetime.now()
        key_name = ':'.join(['cnt', str(ph_id), str(now.hour)])
        obj      = cls.get(db.Key.from_path('AggregateCounterDict', key_name))

        if obj is None or obj.hr.day != now.day:
            obj = cls(key_name=key_name, project=project, count_dict_dump='{}')

        obj.count_dict = json.loads(obj.count_dict_dump)
        return obj

    def dump_and_save(self):
        self.count_dict_dump = json.dumps(self.count_dict)
        return self.put()

    @classmethod
    @transaction
    def update_obj_with_stat(cls, i, stat):
        def updt(cnts, stat):
            for typ in stat:
                for dimp in stat[typ]:
                    for dims in stat[typ][dimp]:
                        if typ not in cnts:
                            cnts[typ] = {}
                        if dimp not in cnts[typ]:
                            cnts[typ][dimp] = {}
                        if dims not in cnts[typ][dimp]:
                            cnts[typ][dimp][dims] = [0, 0]

                        cnts[typ][dimp][dims][0] += stat[typ][dimp][dims][0]
                        cnts[typ][dimp][dims][1] += stat[typ][dimp][dims][1]

        orig = cls.get_or_create_count_obj(i)
        cnts = orig.count_dict
        # todo: timeline update needs to happen differently

        for j in ['aggregate', 'timeline']:
            if j not in cnts:
                cnts[j] = {}
            updt(cnts[j], stat[j])

        return orig.dump_and_save()

    @classmethod
    def update_with_stats(cls, stats):
        for i in stats:
            cls.update_obj_with_stat(i, stats[i])
        return

    def save_to_global_stats(self, proj, stat):
        # todo:
        # save tagp entries.
        return

    @classmethod
    def _aggregate_stats_for_proj(cls, p, till_b4_hr, now, local=False):
        from_hr = p.last_hr                    # last hr when stats were taken
        if from_hr is None:
            from_hr = utils.hr_before(4) # todo: wtf
        from_hr += datetime.timedelta(hours=1)

        log(from_hr, till_b4_hr, now)
        if local:           # just for testing.
            till_b4_hr += datetime.timedelta(hours=1)
            from_hr = utils.hr_before(1)

        while from_hr < till_b4_hr:
            hr_stats = cls.get_hour_stats(p.key().id(), from_hr)
            if hr_stats:
                log('----------')
                logging.info('#### aggregate - [(project) ' + p.name +
                             '  till: ' + str(till_b4_hr) +
                             ']  [(hr) ' + str(from_hr.hour) +']  ' +
                             str(len(hr_stats)))
                aggregate = hr_stats['aggregate']
                timeline = hr_stats['timeline']

                for i in aggregate:
                    Aggregate.save_aggregate(p.key().id(), i, aggregate[i])

                for i in timeline:
                    Timeline.save_timeline(p.key().id(), i, timeline[i])

            p.last_hr = from_hr
            from_hr += datetime.timedelta(hours=1)


    @classmethod
    def aggregate_stats(cls, local=False):
        """Aggregate hourly stats, to the main stats
        """
        now = datetime.datetime.now()
        if now.minute > 15 or local:
            hrd = 0
        else:
            hrd = 1

        till_b4_hr = utils.hr_before(hr_delta=hrd, now=now)

        for p in Project.all().fetch(PROJECT_LIMIT):
            try:
                cls._aggregate_stats_for_proj(p, till_b4_hr, now, local)
            finally:
                p.put()

    @classmethod
    def get_hour_stats(cls, ph_id, from_hr):
        hour = from_hr.hour
        project  = db.Key.from_path('Project', int(ph_id))
        key_name = ':'.join(['cnt', str(ph_id), str(hour)])
        obj = cls.get(db.Key.from_path('AggregateCounterDict', key_name))

        if not obj or obj.hr.day != from_hr.day:
            return None

        return json.loads(obj.count_dict_dump)

    # the updates need to be regulated. Could even be sharded, like
    # counters. Sharding and all should happen behind the sean.

# todo: for each metrics - figure out the dimentions. and then
# join meta-metrics to it.


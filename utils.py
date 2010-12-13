import logging
from datetime import datetime, timedelta

def slashify(*args):
    def fn(s):
        if s[0] == '/':
            s = s[1:]
        if s[-1] == '/':
            s = s[:-1]
        return s
    return '/'+'/'.join([fn(str(s)) for s in args if s!=''])

def dashify(*args):
    return '-'.join([str(i) for i in args])


# time related stuff
def hr_before(hr_delta=0, now=datetime.now()):
    return now - timedelta(hours=hr_delta, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)

def month_start(now=datetime.now()):
    return now - timedelta(days=now.day, hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)

def timedelta_total_hours(td):
    return int((td.seconds + td.days * 24 * 3600) / 3600)

def str2ts(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%d-%H')

def add_hrs(i, ms):
    return timedelta(hours=i) + ms

def month_tag(now=datetime.now()):
    return datetime.strftime(now, '%Y-%m')

def last_month(now=datetime.now()):
    return now - timedelta(days=now.day)

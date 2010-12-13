#!/usr/local/bin/python2.5

import tempfile
import shutil
import re
import os

YUI_COMPRESSOR = 'yuicompressor-2.4.2.jar'

# todo: write script tag with the replaced script.  the file would initially be
# at temporary place.  once all such files are created, read all the htmls and
# copy the script and css files they refer to another direcotory and use it to
# deploy the code.

def ext(path):
    return os.path.splitext(path)[1]

def join(path, *p):
    return os.path.join(path, *p)

def exists(path):
    return os.path.exists(path)

def abspath(path):
    return os.path.abspath(os.path.normpath(path))

def basename(path):
    return os.path.basename(path)

def rm(path):
    return os.remove(path)


class ProcessCommands():
    def __init__(self, dest, scripts, base=''):
        self.dest = dest
        self.base = base
        self.scripts = scripts
        self.data = []
        self.files = []

        if isinstance(scripts, str):
            self.paths = self.get_script_files(scripts)
        elif isinstance(scripts, list):
            self.paths = scripts

        self.paths = [join(base, re.sub(r'^/*', '', p)) for p in self.paths]

    def get_script_files(self, s):
        return [i for i in re.findall(r'.*?<script.*?src="(.*?)"', s, re.DOTALL)]

    def process(self):
        # to be overridden by inherited classes with the act.
        pass

class CombineAndBuild(ProcessCommands):
    def process(self):
        for p in self.paths:
            if not exists(p):
                print ' file doesnt exist: ', p
                return self.paths, self.scripts

            # do operations like minimization etc here.
            self.files.append(p)
            self.data.append(open(p).read())


        extension = ext(self.dest)
        if extension == '':
            self.dest += '.js'

        print 'combining scripts to!',  self.dest.replace(self.base, '')
        # f = open(self.dest, 'w')
        # f.write('\n'.join(self.data))
        # f.close()

        # --
        tmp_file, tmp_file_name = tempfile.mkstemp()
        os.close(tmp_file)

        tmp_file = open(tmp_file_name, 'w')
        tmp_file.write('\n'.join(self.data))
        tmp_file.close()

        os.system("%s %s --type js -o %s" % (YUI_COMPRESSOR, tmp_file_name, self.dest))
        os.unlink(tmp_file_name)
        # --

        return self.paths, '<script src="%s"></script>' % (self.dest.replace(self.base, ''))


def rel_path(base, target):
    # @see http://code.activestate.com/recipes/302594-another-relative-filepath-script/
    b_list = (abspath(base)).split(os.sep)
    t_list = (abspath(target)).split(os.sep)

    for i in range(min(len(b_list), len(t_list))):
        if b_list[i] <> t_list[i]: break
    else:
        i += 1

    rel_list = [os.pardir] * (len(b_list)-i) + t_list[i:]

    return join(*rel_list)

class ProcessBuildComments():

    def __init__(self, path, base='', nbase=''):
        f = open(path)

        if f:
            self.path = path
            self.base = base
            self.nbase = nbase
            self.body = f.read()
            self.handle_comment()
        else:
            # todo: error
            print 'couldnt find the file', path

    def build_group(self, m, f, s):
        klass = ''.join([i.capitalize() for i in m.split('_')])
        k = globals()[klass](f, s, self.base)
        if k:
            rep = k.process()
        return rep

    def handle_comment(self):
        # find all javascript build groups.
        regexp = r'.*?<!-- *@([a-z_]*) *([a-z_]*) *-->(.*?)<!-- *@end *-->.*?'
        matches = re.findall(regexp, self.body, re.DOTALL)

        if not len(matches):
            return []

        # find the script files mentioned in group. and do the mentioned corresponding action.
        for m, f, s in matches:
            paths, rep = self.build_group(m, join(self.nbase, f), s)
            if rep:
                # change the body to include the result of operation done on build group.
                regexp = re.compile(r'<!-- *@%s *%s *-->(.*?)<!-- *@end *-->' % (m, f), re.DOTALL)
                self.body = re.sub(regexp, rep, self.body, re.DOTALL)

        self.body = self.body.replace('REPLACE_WITH_APP_STATE', '"live"')


        dst_file = join(self.nbase, rel_path(self.base, self.path))

        print 'writing the modified html file to: ', dst_file
        f = open(dst_file, 'w')
        f.write(self.body)
        f.close()


def rec_find_files(base, ext='html', ignore=[]):
    "Find files with the 'ext' under 'base' ignoring the 'ignore' directories "
    paths = []
    for root, dirs, files in os.walk(base):
        for name in files:
            if re.match(r'.*\.%s$' % ext, join(root, name)):
                paths.append(join(root, name))

        ignore = [join(base, i) for i in ignore]

        if '.git' in dirs:
            dirs.remove('.git')

        for d in dirs:
            if join(root, d) in ignore:
                print 'ignoring: ', join(root,d)
                dirs.remove(d)
    return paths

def del_unused_files(base, paths):
    for root, dirs, files in os.walk(base):
        for name in files:
            p = join(root, name)
            if not abspath(p) in paths:
                rm(p)

def del_unwanted_files(base):
    for root, dirs, files in os.walk(base):
        for name in files:
            p = join(root, name)
            if exists(p) and ext(p) == '.pyc':
                rm(p)

def copy_to_temp_directory(base):
    dst = join(tempfile.mkdtemp(), basename(base))
    shutil.copytree(base, dst)
    print dst
    return dst

def get_script_paths(f):
    return [re.sub(r'^/*', '', i) for i in re.findall(r'.*?<script.*?src="(.*?)"', open(f).read(), re.DOTALL)]



def setup_tmp_deploy(base):
    tmp = copy_to_temp_directory(abspath(base))
    bdir = join(tmp, 'build')
    ignore = ['js']
    paths = []

    # setup clean build
    print tmp, bdir
    if exists(bdir):
        shutil.rmtree(bdir)
    os.makedirs(bdir)

    print '[base:', base, ']  [dest:', tmp, ']  [build dir:', bdir

    for p in rec_find_files(tmp, ext='html', ignore=ignore):
        ProcessBuildComments(p, tmp, bdir)

        paths.extend(get_script_paths(p))

    # cleanup
    for i in ignore:
        del_unused_files( join(tmp, i), [join(tmp, p) for p in paths])
    del_unwanted_files(tmp)

    return tmp

def main(base):
    dply = setup_tmp_deploy(base)

    os.system('cd %s; cd ..; echo `pwd`; appcfg.py -e mail.ciju.cherian@gmail.com update perf-hier' % dply)

if __name__ == '__main__':

    main('/home/ciju/data/work/perf-hier/')
    # copy the whole src directory.
    # make a temporary directory.
    # copy and create the needed files in the temporary directory.
    # remove the directories no longer needed.
    # copy the files in temp dir, to where they belong.

    # write the index file according to instructions.


def rm_key(k, s):
    os = json.loads(s)
    ns = {}
    for i in os:
        for j in os[i]:
            if not re.match(r'^'+k, j):
                if not i in ns:
                    ns[i] = {}
                ns[i][j] = os[i][j]
                print i,j
    return json.dumps(ns)

def rm_root(root, stat):
    ostat = json.loads(stat)
    nstat = {}
    for i in ostat:
        if not re.match('^'+root, i):
            nstat[i] = ostat[i]
    print i
    return json.dumps(nstat)


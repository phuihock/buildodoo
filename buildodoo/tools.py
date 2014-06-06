from fabric.api import local
from fabric.contrib.console import confirm
from fabric.utils import warn
import ConfigParser
import fabric.api
import os
import re
import vcs

SPEC = re.compile("(.*?)(\[(.*)\])?$")
ROOT = os.path.abspath('.')
config = ConfigParser.ConfigParser()
cfg = 'instance.cfg'
if os.path.isfile(cfg):
    ROOT = os.path.dirname(os.path.abspath(cfg))
    config.read(cfg)

addons_path = []
def addons_path_adder(cmd, path):
    addons_path.append(path)

class Collector(list):
    def __call__(self, cmd, out):
        if cmd == 'pwd':
            out = out.replace(ROOT + '/', '')
        self.append(out)

def process_repo(op, name, repo_name, repo_spec, stack, collector=None, multiline=False):
    mo = SPEC.match(repo_spec)
    if mo:
        repo, _, protocol = [g.strip() for g in mo.groups()]
        repo = os.path.join(ROOT, repo)

    if config.has_option('revisions', repo):
        rev = config.get('revisions', repo)
    else:
        rev = vcs.revisions['last:1'].get(protocol)

    cmd = vcs.commands[op]
    if multiline:
        repo_name = os.path.join(repo_name, os.path.basename(repo))
        stack.append(('local', 'mkdir -p ' + repo_name))

    stack.append((('lcd', repo_name), ('local', 'pwd', collector), ('local', lambda: cmd[protocol] % {
        'root': ROOT,
        'name': name,
        'repo': repo,
        'relcwd': collector[-1],
        'rev': rev,
    }, collector)))

def _process_server(op, name='instance', collector=None):
    stack = []
    stack.append(('local', 'mkdir -p server'))
    repo_name = config.get(name, 'server')
    repo_spec = config.get('repo', repo_name)
    process_repo(op, name, repo_name, repo_spec, stack, collector=collector)
    return stack

def _process_addons(op, name='instance', collector=None):
    stack = []
    stack.append(('local', 'mkdir -p addons'))
    stack.append(('lcd', 'addons'))
    addons = config.get(name, 'addons')
    for addon_spec in addons.splitlines():
        mo = SPEC.match(addon_spec)
        addon_name, _, subdir = [g.strip() for g in mo.groups()]
        dest = os.path.normpath(os.path.join(addon_name, subdir))
        stack.append(('local', 'mkdir -p ' + addon_name))
        if not config.has_option('repo', addon_name):
            warn("'%s' is not found in section 'repo', but added to addons_path anyway." % addon_name)
            addons_path_adder(None, os.path.join(ROOT, dest))
        else:
            repos = config.get('repo', addon_name)
            repo_spec = [l for l in repos.splitlines() if l]
            multiline = len(repo_spec) > 1
            for spec in repo_spec:
                process_repo(op, name, addon_name, spec, stack, collector=collector, multiline=multiline)
            stack.append((('lcd', dest), ('local', 'pwd', addons_path_adder)))
    return stack

def _process(op, name='instance'):
    collector = Collector()
    s1 = _process_server(op, name, collector)
    s2 = _process_addons(op, name, collector)
    _exec((('local', 'mkdir -p %s' % name), ('lcd', name), s1, s2), fabric.api)
    _print_captured(collector, op)
    return collector

def _do(f, ctx):
    func = getattr(ctx, f[0])
    if len(f) == 3 and hasattr(f[2], '__call__'):
        if hasattr(f[1], '__call__'):
            expr = f[1]()
        else:
            expr = f[1]
        out = func(expr, capture=True)
        f[2](f[1], out)
    else:
        out = func(f[1])
    return out

def _exec(stack, ctx):
    for i, f in enumerate(stack):
        if isinstance(f, (tuple, list)):
            if isinstance(f[0], str):
                out = _do(f, ctx)
                if out and hasattr(out, '__enter__'):
                    with out:
                        _exec(stack[i + 1:], ctx)
                    break
            else:
                _exec(f, ctx)

def _parse_captured(buf):
    groups = []
    for i in xrange(0, len(buf), 2):
        groups.append((buf[i], buf[i+1]))
    return groups

def _print_captured(buf, op):
    groups = _parse_captured(buf)
    for g in groups:
        print '[%s] location: %s' % (op, g[0])
        out = g[1]
        if out:
            print '[%s] %s' % (op, out)

def checkout():
    abort = False
    if os.path.exists('instance'):
        abort = not confirm("'instance' already exists. Do you want to remove it and continue?")

    if not abort:
        local('rm -rf instance')
        _process('checkout')
        with open('instance.addons.cfg', 'w') as f:
            f.write("""[options]
addons_path = %s""" % ','.join(addons_path))

def status():
    _process('status')

def revno():
    _process('revno')

def export():
    abort = False
    if os.path.exists('build'):
        abort = not confirm("'build' already exists. Do you want to remove it and continue?")

    if not abort:
        local('rm -rf build/instance')
        _process('export')

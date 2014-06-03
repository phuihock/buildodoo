from fabric.contrib.console import confirm
from fabric.state import output
import ConfigParser
import fabric.api
import os
import re
import vcs

SPEC = re.compile("(.*?)(\[(.*)\])?$")

config = ConfigParser.ConfigParser()
cfg = 'instance.cfg'
if os.path.isfile(cfg):
    config.read(cfg)

addons_path = []
def addons_path_adder(path):
    addons_path.append(path)

def process_repo(op, repo_name, repo_spec, stack, collector=None, multiline=False):
    mo = SPEC.match(repo_spec)
    if mo:
        target, _, protocol = [g.strip() for g in mo.groups()]

    params = {
        'repo': target,
        'rev': '',
    }

    if config.has_option('revisions', target):
        rev = config.get('revisions', target)
        params['rev'] = '-r ' + rev

    cmd = vcs.commands[op]
    if multiline:
        repo_name = os.path.join(repo_name, os.path.basename(target))
        stack.append(('local', 'mkdir -p ' + repo_name))

    stack.append((('lcd', repo_name), ('local', 'pwd', collector), ('local', cmd[protocol] % params, collector)))

def _process_server(op, name='instance', collector=None):
    stack = []
    stack.append(('local', 'mkdir -p server'))
    repo_name = config.get(name, 'server')
    repo_spec = config.get('repo', repo_name)
    process_repo(op, repo_name, repo_spec, stack, collector=collector)
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
        repos = config.get('repo', addon_name)

        repo_spec = [l for l in repos.splitlines() if l]
        multiline = len(repo_spec) > 1
        for spec in repo_spec:
            process_repo(op, addon_name, spec, stack, collector=collector, multiline=multiline)
        stack.append((('lcd', dest), ('local', 'pwd', addons_path_adder)))
    return stack

def _process(op, name='instance'):
    buf = []
    def collector(out):
        buf.append(out)

    s1 = _process_server(op, name, collector)
    s2 = _process_addons(op, name, collector)
    _exec((('local', 'mkdir -p %s' % name), ('lcd', name), s1, s2), fabric.api)
    _print_captured(buf, op)
    return buf

def _do(f, ctx):
    func = getattr(ctx, f[0])
    if len(f) == 3 and hasattr(f[2], '__call__'):
        out = func(f[1], capture=True)
        f[2](out)
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
    if output.debug:
        groups = _parse_captured(buf)
        for g in groups:
            print '[%s] location: %s' % (op, g[0])
            out = g[1]
            if out:
                print '[%s] %s' % (op, out)

def checkout():
    _process('checkout')

def status():
    _process('status')

def revno():
    _process('revno')

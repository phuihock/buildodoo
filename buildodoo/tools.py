from fabric.contrib.console import confirm
from fabric.api import *

import ConfigParser
import re
import os
import vcs

config = ConfigParser.ConfigParser()
config.read('instance.cfg')
spec = re.compile("(.*?)(\[(.*)\])?$")

def command(cmd, name, repo, subdir='.', multilines=False):
    mo = spec.match(repo)
    if mo:
        g1, g2, g3 = [g.strip() for g in mo.groups()]
        args = {
            'repo': g1,
            'rev': '',
        }

        if config.has_option('revisions', name):
            revno = config.get('revisions', name)
            args['rev'] = '-r ' + revno

        cmd = vcs.commands[cmd][g3]
        if multilines:
            dst = os.path.join(name, os.path.basename(g1))
        else:
            dst = name
        local('mkdir -p %s' % dst)
        with lcd(dst):
            out = local(cmd % args, capture=True)
            with lcd(subdir):
                path = local('pwd', capture=True)
                return path, args['repo'], out

def project(cmd):
    outputs = []
    local('mkdir -p instance')

    with lcd('instance'):
        server_repo = config.get('instance', 'server')
        result = command(cmd, 'server', config.get('repo', server_repo))
        outputs.append(result)

        local('mkdir -p addons')
        with lcd('addons'):
            addons = config.get('instance', 'addons')
            for addon in addons.splitlines():
                mo = spec.match(addon)
                if mo:
                    g1, g2, g3 = [g.strip() for g in mo.groups()]
                    name, subdir = g1, g3
                    bundle = config.get('repo', name).splitlines()
                    for r in bundle:
                        result = command(cmd, name, r, subdir, len(bundle) > 1)
                        outputs.append(result)
    return outputs

def init():
    with settings(warn_only=True):
        if not local('test -d instance').failed:
            local('mv instance instance_$(date +%Y%m%d.%H%M%S)')

        addons_path = []
        for result in project('checkout'):
            path, repo, out = result
            if path not in addons_path:
                addons_path.append(path)

        with open('openerp.instance.cfg', 'w') as f:
            f.write("""[options]
addons_path = %s""" % ','.join(addons_path))


def freeze():
    for result in project('revno'):
        path, repo, revno = result
        print '%s = %s' % (repo, revno)

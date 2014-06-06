from buildodoo import tools
from nose import tools as t
import ConfigParser
import io
import shutil
import os
import subprocess


ROOT = os.path.abspath('.')

def assert_stack_eq(frame, a, msg=None):
    parsed_tree = []
    for p in frame:
        if isinstance(p, (tuple, list)):
            op = (p[0], p[1])
            if len(p) == 3 and hasattr(p[2], '__call__'):
                op += (p[2].__name__,)
            parsed_tree.append(op)
    t.eq_(parsed_tree, a)

def _basic_cfg():
    tools.config = ConfigParser.ConfigParser()
    tools.config.readfp(io.BytesIO("""
[instance]
server = server
addons =

[repo]
server = %(repo)s [git]
""" % {'repo': ROOT}))


def _single_addon_cfg():
    tools.config = ConfigParser.ConfigParser()
    tools.config.readfp(io.BytesIO("""
[instance]
server = server
addons = one [.]

[repo]
server = %(repo)s [git]
one = %(repo)s [git]
""" % {'repo': ROOT}))


def _single_addon_rev_cfg():
    tools.config = ConfigParser.ConfigParser()
    tools.config.readfp(io.BytesIO("""
[instance]
server = server
addons = one [.]

[repo]
server = %(repo)s [git]
one = %(repo)s [git]

[revisions]
%(repo)s = e3224b1
""" % {'repo': ROOT}))


def _multi_addons_cfg():
    tools.config = ConfigParser.ConfigParser()
    tools.config.readfp(io.BytesIO("""
[instance]
server = server
addons = one [.]
         two [tests]

[repo]
server = %(repo)s [git]
one = %(repo)s [git]
two = %(repo)s [git]
""" % {'repo': ROOT}))


def _arbitrary_addon_cfg():
    tools.config = ConfigParser.ConfigParser()
    tools.config.readfp(io.BytesIO("""
[instance]
server = server
addons = tests [addons]

[repo]
server = %(repo)s [git]
""" % {'repo': ROOT}))

def _prepare():
    shutil.rmtree('instance', True)

def _cleanup():
    shutil.rmtree('instance', True)

@t.with_setup(_prepare, _cleanup)
@t.with_setup(_basic_cfg)
def test_instance_server():
    tools._process('checkout')
    assert os.path.exists('instance/server/EXISTS')


@t.with_setup(_prepare, _cleanup)
@t.with_setup(_single_addon_cfg)
def test_single_addon():
    tools._process('checkout')
    assert os.path.exists('instance/addons/one/EXISTS')


@t.with_setup(_prepare, _cleanup)
@t.with_setup(_single_addon_rev_cfg)
def test_single_addon_rev():
    tools._process('checkout')
    output = subprocess.check_output(['git', '--git-dir=instance/addons/one/.git', 'rev-parse', '--short', 'HEAD']).strip()
    t.eq_(output, "e3224b1")


@t.with_setup(_prepare, _cleanup)
@t.with_setup(_multi_addons_cfg)
def test_multi_addons():
    tools._process('checkout')
    assert os.path.exists('instance/addons/one/EXISTS')
    assert os.path.exists('instance/addons/two/EXISTS')

@t.with_setup(_prepare, _cleanup)
@t.with_setup(_arbitrary_addon_cfg)
def test_arbitrary_addon():
    tools._process('checkout')
    assert ('%s/tests/addons' % tools.ROOT) in tools.addons_path

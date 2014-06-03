from buildodoo import tools
from nose import tools as t
import ConfigParser
import io
import shutil
import os


ROOT = os.path.normpath('..')

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
%(repo)s = 1
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


@t.with_setup(_basic_cfg)
def test_instance_server():
    stack = tools._process_server('checkout')
    assert_stack_eq(stack[-1], [('lcd', 'server'), ('local', 'pwd'), ('local', 'git clone .. . ')])


@t.with_setup(_single_addon_cfg)
def test_single_addon():
    stack = tools._process_addons('checkout')
    assert_stack_eq(stack[-2], [('lcd', 'one'), ('local', 'pwd'), ('local', 'git clone .. . ')])
    assert_stack_eq(stack[-1], [('lcd', 'one'), ('local', 'pwd', 'addons_path_adder')])


@t.with_setup(_single_addon_rev_cfg)
def test_single_addon_rev():
    stack = tools._process_addons('checkout')
    assert_stack_eq(stack[-2], [('lcd', 'one'), ('local', 'pwd'), ('local', 'git clone .. . -r 1')])
    assert_stack_eq(stack[-1], [('lcd', 'one'), ('local', 'pwd', 'addons_path_adder')])


@t.with_setup(_multi_addons_cfg)
def test_multi_addons():
    stack = tools._process_addons('checkout')
    assert_stack_eq(stack[-2], [('lcd', 'two'), ('local', 'pwd'), ('local', 'git clone .. . ')])
    assert_stack_eq(stack[-1], [('lcd', 'two/tests'), ('local', 'pwd', 'addons_path_adder')])

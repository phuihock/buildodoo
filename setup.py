from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='buildodoo',
      version='0.1',
      author='Chang Phui-Hock',
      author_email='phuihock@codekaki.com',
      description='A set of common fabric tasks to build, manage and release Odoo/OpenERP project',
      license='AGPL',
      long_description=read('README.rst'),
      classifiers=[],
      packages=['buildodoo'],
      )

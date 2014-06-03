INTRODUCTION
============

This project contains a common set of Fabric tasks to manage, freeze and release Odoo/OpenERP project. It is built as a quickfix to
an itch.

WARNING
-------
This is still very much experimental. If you need a mature project to work with, checkout `anybox.recipe.buildout <http://docs.anybox.fr/anybox.recipe.openerp/trunk>`_
recipe.

INSTALLATION
------------
::

  $ pip install fabric
  $ pip install -e git+https://github.com/codekaki/buildodoo#egg=buildodoo


USAGE
-----
Edit ``fabfile.py``. Example::

  from buildodoo.tools import init, freeze

Edit ``instance.cfg``. Example::

  [instance]
  server = server
  addons = 7.0 [.]
           web [addons]
           pentaho-reports [openerp_addon]  ; add subdir 'openerp_addon' to addons_path
           custom [.]  ; grouping of multiple standalone addons is possible, add 'custom' to addons_path

  [repo]
  server = ~/Work/lp/openobject-server/7.0 [bzr]
  7.0 = ~/Work/lp/openobject-addons/7.0 [bzr]
  web = ~/Work/lp/openerp-web/7.0 [bzr]
  pentaho-reports = ~/Work/lp/extras/Pentaho-reports-for-OpenERP [git]
  custom = ~/Work/lp/custom/hr_roster [bzr]
           ~/Work/lp/custom/hr_employment [bzr]
           ~/Work/lp/custom/hr_work_day [bzr]
           
  [revisions]
  ~/Work/lp/openerp-web/7.0 = last:1
           
Lastly, checkout the project like this::

  $ fab checkout

This will create a new instance in ``instance`` directory and print complete ``addons_path`` to the console.
  
To display revisions of all checkouts::

  $ fab revno
  
To prepare the project for deployment::
  
  $ fab export
  
This will export the current project to ``build/instance`` directory.

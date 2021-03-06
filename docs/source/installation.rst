.. _installation:

Installation
============

.. note:: I **highly** recommend using virtualenv, but nothing prevents you
          installing it into the root system

Requirements
------------

When installing this package using easy_install, it will build the MySQL and
Postgres clients. So you'll need the necessary headers, plus gcc on your
machine.

For Ubuntu, run the following::

   sudo apt-get install libmysqlclient-dev libpq-dev python-dev \
                           build-essential

Installation procedure
----------------------

- Download the latest package from http://www.github.com/exhuma/pickup
  I recommend using the latest tagged version, but if you want bleeding
  edge, you may also download the "master" branch.

- untar the package::

     tar xzf exhuma-pickup-<version number+hash>.tar.gz

- enter the folder::

     cd exhuma-pickup-<version number+hash>

When not using virtualenv, you may skip this section
----------------------------------------------------

.. note:: If you don't have virtualenv,
          run the following::

             apt-get install python-setuptools && easy_install virtualenv

- create a virtualenv::

     virtualenv --no-site-packages /path/to/your/env

- activate the environment::

     source /path/to/your/env/bin/activate

Without virtualenv
------------------

- run the installer::

   python setup.py install

Finished & Trying things out
----------------------------

The script is now installed in you system's binary path as "pickup". When using
virtualenv, this will be ``/path/to/your/env/bin``, otherwise it will most
likely be ``/usr/local/bin``

You may now deactivate the virtualenv by entering ``deactivate``. In the future
it will no longer be necessary to activate the environment manually. The
executable script will run automatically in the proper environment.

To see if everything worked as expected, you may run::

   /path/to/your/env/pickup --help

or simply (if it's on your ``$PATH``)::

   pickup --help


.. pickup documentation master file, created by
   sphinx-quickstart on Sun Nov  7 19:27:05 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pickup
==================================

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   configuration
   available_plugins
   writing_plugins
   how_and_why
   glossary


Introducing Pickup
------------------

Pickup is a **modular backup script** written completely in Python.

The source code is available on `the github project page
<https://github.com/exhuma/pickup>`_

The core of the application is the executable ``pickup.py`` and a python script
used as config file.  This core does not include *any* code related as to *how*
a backup from a given source should be created. This logic is stashed away in
modules. This has the advantage that it's very easy to add support for a new
"data source" or to change the behaviour of an existing component.

The backup target is created in the exact same way. For the exact same reason.
The only drawback, is that backups need to be created in a "staging area" first
before they are deployed to a target. This is done because some targets (like
rsync) work best if you can feed them one folder containing everything. It
would be a waste to run rsync on each file separately.

Example Configuration
---------------------

.. include:: config_examples/basic.rst

See :ref:`configuration` for more details and examples.

Example Execution
-----------------

Take the above configuration and save it anywhere you like. You can execute it
by running::

   python pickup.py -c /path/to/config_file.py

Or, if you installed it into you system (see :ref:`installation`)::

   /path/to/pickup -c /path/to/config_file.py

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


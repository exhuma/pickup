.. pickup documentation master file, created by
   sphinx-quickstart on Sun Nov  7 19:27:05 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pickup
==================================

Pickup is a **modular backup script** written completely in Python.

The source code is available on `the github project page
<https://github.com/exhuma/pickup>`_

The core of the application is the executable ``pickup.py`` and the config file
``config.py``.  This core does not include *any* code related as to *how* a
backup from a given source should be created. This logic is stashed away in
modules. This has the advantage that it's very easy to add support for a new
"data source" or to change the behaviour of an existing component.

The backup target is created in the exact same way. For the exact same reason.
The only drawback, is that backups need to be created in a "staging area" first
before they are deployed to a target. This is done because some targets (like
rsync) work best if you can feed them one folder containing everything. It
would be a waste to run rsync on each file separately.

Another advantage of the modular design is backwards compatibility. The core
should do a fairly good job with that. I'll take a leap of faith and say, it
should work with Python 2.3. Maybe even 2.2, but I haven't checked. The modules
themselves are another story. Some modules may require third-party modules (for
example: the postgres module requires psycopg2) and may not be as backwards
compatible.

Everything that is currently available should work fine with Python 2.3 and up.

Contents:

.. toctree::
   :maxdepth: 2

   configuration
   available_plugins
   writing_plugins

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


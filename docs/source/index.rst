.. pickup documentation master file, created by
   sphinx-quickstart on Sun Nov  7 19:27:05 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pickup
==================================

Why (History)
~~~~~~~~~~~~~

   Why am I writing this script and why would you want to use it?

I needed a simple way to create backups of a couple of folders, a few MySQL and
PostgreSQL databases and store the created files on a remote FTP site. I
implemented this using a small bash script using ``ncftp`` to store them on the
FTP site.

`zmanda backup <http://www.zmanda.com/>`_ Seemed to be a bit too much at the
time.

Over time the script became more and more generalised. And as a result more and
more unreadable. After it started using bash arrays quite heavily the resulting
syntax really got on my nerves. Recently I needed to create backups in a
similar fashion on another server. And there the fun started. A couple of
problems:

   - One server used a standard debian PostgreSQL installation, the other
     didn't. But the script used a ``psql`` parameter (``--cluster``) which is
     only available on the default debian installation.

   - A couple of minor things did not work exactly the same way on both
     servers.

Additionally, the script had one major annoyance from the beginning:

``ncftp`` writes all server messages to ``stdout``. So, to see errors, I had to
refrain from redirecting ``ncftp``'s output to ``/dev/null``. But that in turn
meant that I received a cron-mail on each execution. Eventually, I redirected
the FTP output to ``/dev/null``. That way I only got cron-mails when something
else went wrong. But I had to check the FTP regularly to see if the backups
arrived correctly.

I always wanted to fix these issues, and add a couple more functionalities to
the script. But given the complexity it already had, I thought it be time to
rewrite it using a different scripting language. I've chosen Python as language
of choice. A couple of reasons:

   - It's the language I am currently most proficient in

   - It's available on pretty much any standard Linux installation (other
     choice could have been perl.)

   - It is very dynamic and let's me write a modular application easily.

   - The syntax is very concise!

Introducing Pickup
~~~~~~~~~~~~~~~~~~

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

.. note:: I was thinking of a way to get rid of the staging area and "stream"
   the data directly to the target location. But this would require me to
   rewrite a lot of the already existing code. For now, I am focussing on the
   completion of the current version. Using a temporary staging area does
   currently not pose a problem for me, so I'll leave this for the future. The
   main Idea was: Let the generator create and return a file-like object and
   pass this directly to the target. While this won't work with everything
   without an intermediate step, it could still be very useful.

Another advantage of the modular design is backwards compatibility. The core
should do a fairly good job with that. I'll take a leap of faith and say, it
should work with Python 2.3. Maybe even 2.2, but I haven't checked. The modules
themselves are another story. Some modules may require third-party modules (for
example: the postgres module requires psycopg2) and may not be as backwards
compatible.

Everything that is currently available should work fine with Python 2.3 and up.

Concepts
========

The application works in two main steps:

   - Generate the backup data (DB dumps, archive generation, ...)

     See :term:`generator`

   - "publish" the generated files to one or more targets.

     See :term:`target`

Usage
=====

The config file specifies what to backup (``GENERATORS``), and where to store
it (``TARGETS``). See :ref:`configuration` for more information on the general
configuration.

The generators and targets are defined in python module inside generator_profile and
target_profiles.  For a list of available generators and targets see
:ref:`available_plugins`

If something is missing the list of plugins, you can easily write a new plugin
with only minimal python knowledge. See :ref:`writing_plugins` for more
information.

Application output uses the default python logging module. All informational
messages are routed to stdout, and all errors/warnings are routed to stderr.
This is useful for cron jobs: redirecting stdout to /dev/null still lets
important messages through, so cron can take the appropriate steps (send
mails?)

Debugging messages are logged to a auto-rotating file inside the "logs"
directory. This provides some semi-persistent storage. If something went wrong
and you redirected stdout (or deleted the cron-mails), you still may find some
useful info in that file.

Rough Roadmap
=============

The main goal is to have a script which has all the features that I had in my
previous bash script. These features are:

  - **[DONE]** Folder backups (split and simple)

  - **[DONE]** Push to folder

  - **[DONE]** Backup PostgreSQL

  - **[DONE]** Docs

  - **[DONE]** Backup MySQL

  - **[DONE]** Push to FTP

  - Remove old files (using the retention value)

  - Push to a remote host via SSH

Additional items on the todo list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - Move logging configuration out of the code

Table of Contents
=================

Contents:

.. toctree::
   :maxdepth: 2

   configuration
   available_plugins
   writing_plugins
   glossary

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


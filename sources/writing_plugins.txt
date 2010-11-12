.. _writing_plugins:

Using Plugins
=============

The core uses the plugin filename as profile name. So if you create a new
plugin named ``foobar.py``, then you can use it in the config file as ``profile
= "foobar"``. It's as simple as that.

Writing Plugins
===============

You can do pretty much anything with these plugins. As you can chain multiple
sources or targets, nothing holds you back for writing a plugin that won't
create real backups. This might sound useless, but, you could for example write
a source plugin which lists all files in a folder, and save that list in the
staging area. This won't be a valid backup of the data, but may prove useful
nonetheless.

Both source and target plugins follow the same standard. In a nutshell:

   - A "init" function initialises the plugin. This is called for each
     source/target

   - A "run" function performs the actual job of creating/publishing the backup

   - A source plugin is resposible to create backup files inside the "staging
     area".

   - A target plugin is responsible to publish/push the files inside the
     staging area to another location.

General housekeeping
--------------------

File Names
~~~~~~~~~~

When creating filenames, it is recommended to use `os.path.join
<http://docs.python.org/library/os.path.html#os.path.join>`_, which will ensure
platform independent filenames.

The minimal example below makes use of this module.

Documentation
~~~~~~~~~~~~~

The config file used by the end-users strongly depends on the config values
used in the plugins. As such, it would be very nice if these values are well
documented. The project used the module level docstrings in the auto-generated
documentation (the one you are reading just now). So everything needed to setup
the plugin should be documented there.

It is recommended to add a code-block depicting an example configuration
section for the module. This will make the generated documentation easier to
read and will provide simple copy/paste templates to users.

Look at the available module's source code for examples.

Logging
~~~~~~~

Avoid ``print`` statements at all costs. *Especially* for error messages. The
proper way to print output is to use the logging module. Everything related to
logging is configured for you in the core. So all you need to do is::

   import logging
   LOG = logging.getLogger(__name__)

and then make the appropriate calls to::

   LOG.debug(message)
   LOG.info(message)
   LOG.warning(message)
   LOG.error(message)
   LOG.critical(message)
   LOG.exception(the_exception_instance)

API version
~~~~~~~~~~~

Before executing a plugin, the core checks the API version against it was
developed. If the core changes, and if, as a consequence, changes are necessary
or recommended in the plugin, the application will let you know:

   - Plugin execution is aborted for major changes
   - Warnings are issued for minor changes

The version information needs to be defined in a field named ``API_VERSION``
and must be a tuple of (major_number, minor_number).

Example minimal setup
~~~~~~~~~~~~~~~~~~~~~

.. note:: This example also makes use of ``os.path.join``. It is recommended to
   add this method to create filenames, which will ensure platform independent
   file names. See `os.path.join
   <http://docs.python.org/library/os.path.html#os.path.join>`_ for more info!

.. code-block:: python

   """
   This is the module-level docstring
   """
   import logging
   from os.path import join
   LOG = logging.getLogger(__name__)
   API_VERSION = (1,0)

   def init(source_dict):
      LOG.debug("Hello, I was initialised with %s" % source_dict)

   def run(staging_area):
      LOG.info("Running on %s" % staging_area)
      file_handle = open(join(staging_area, "helloworld.txt"), "w")
      file_handle.write( "Hello World!\n" )
      file_handle.close()

Configuration Values
--------------------

init
~~~~

The core will pass a dictionary to the ``init`` method before executing ``run``.
This dictionary is the same as the one specified in the config file. So, for
example if a source (or target) is configured as follows::

   [ ...,
   dict(
      name = "mysource",
      profile = "my_plugin_module",
      config = dict(
         a = 1,
         b = 2
         )
      ),
     ... ]

Then the dictionary passed to the ``init`` method will be::

   { 'a': 1, 'b': 2 }

run
~~~

When executing ``run``, the core will pass the folder name of the "staging area".

Writing Source Plugins
----------------------

A source plugin represents a type of data that needs to be included in the
backup. After calling ``run``, the plugin must have created a file inside the
staging area. Otherwise the backup will be lost.

Writing Target Plugins
----------------------

A target plugin represents a destination into which the backups will be
"published" (or "pushed"). The ``run`` method receives the "staging area" as
parameter. At the end of the run, all files inside that folder should be in the
target location (as specified in the config).


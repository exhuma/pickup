.. _configuration:

Configuration
=============

The configuration file is a python file itself. All values are stored as simple
python dictionaries or variables.

Basic example
-------------

In its most simple form, a config file to
backup one folder could look like this::


   CONFIG_VERSION = (1,0)
   STAGING_AREA = "staging"
   SOURCES = [{
         'name': '/var/www',
         'profile': 'folder',
         'config': {
            'path': '/var/www',
            'split': True,
            }}]

   TARGETS = [{
         'name': "local",
         'profile': "folder",
         'config': {
            'path': "/path/to/target",
            }}]

Required values
---------------

The following values must be specified:

**CONFIG_VERSION**
   This is used by the core application to determine if it knows how to read
   the config file. If this value is incorrect, the core will issue
   errors/warnings.

   The value is a tuple representing a major and minor number.

   It follows the following rule:

      - If an application change *requires* a change in the config, the major
        number will increase.
      - If a change is made in the application which will still be able to
        function with an old config version, but may benefit from new fields,
        then the minor number will increase.

**STAGING_AREA**
   A *temporary* folder. All backup files will be created in that folder before
   pushed into the targets.

**SOURCES**
   A list of backup sources. The sources will be processed in the same order as
   they appear in the config file. Each source must have the following fields:

      ``name``
         The name of the source (Mainly used to display it in the logs)

      ``profile``
         Definition of the nature of the source. Can be a folder, database, or
         anything supported by the underlying source plugins.

      ``config``
         Config values for the source profile. These fields depend on the
         underlying plugin.

**TARGETS**
   A list of backup targets. The targets will be processed in the same order as
   they appear in the config file. Each source must have the following fields:

      ``name``
         The name of the target (Mainly used to display it in the logs)

      ``profile``
         Definition of the nature of the target. Can be a folder, ftp, or
         anything supported by the underlying target plugins.

      ``config``
         Config values for the target profile. These fields depend on the
         underlying plugin.

Advanced Example
----------------

As the config file is a python script, you can do pretty much everything you
want inside. The main differences are:

   - Use of comments
   - example use of an import
   - A string replacement is used in the ``rsync`` target
   - Instead of writing dictionaries using the ``{`` and ``}`` syntax, they are
     constructed using the ``dict()`` builtin. This makes it easier to write
     (and maybe even to read as well).

.. note::
   Not all source and target plugins listed in the following config file are
   available yet!

Advanced config file::

   from datetime import timedelta

   # Config version (major, minor)
   CONFIG_VERSION = (1,0)

   # A custom variable. Not used by the application itself, but used here, in
   # the config script!
   THE_BACKUP_DIR = "/var/backups/data"

   # All backups will be created in this folder before being deployed to the
   # targets
   STAGING_AREA = "staging"

   # Backup Sources. They will be processed in order
   #
   # Details on the config values should be documented in the source modules
   SOURCES = [
      dict(
         name = 'MySQL',
         profile = 'mysql',
         config = dict(
            # user should have full priviledges on everything
            user = "root",
            password = "mysecretpassword"
            ),
         ),
      dict(
         name = 'PostgreSQL 8.4',
         profile = 'postgres',
         config = dict(
            host = 'localhost',
            database = '*', # using '*' will dump all dbs
            port = 5432
            ),
         ),
      dict(
         name = '/var/www',
         profile = 'folder',
         config = dict(
            path = '/var/www',
            split = True,
            )
         ),
      dict(
         name = '/var/git',
         profile = 'folder',
         config = dict(
            path = '/var/git',
            split = True,
            )
         ),
      dict(
         name = '/var/mail',
         profile = 'folder',
         config = dict(
            path = '/var/mail',
            )
         ),
      dict(
         name = '/etc/apache2',
         profile = 'folder',
         config = dict(
            path = '/etc/apache2',
            )
         ),
      dict(
         name = '/home/exhuma',
         profile = 'folder',
         config = dict(
            path = '/home/exhuma',
            )
         ),
      ]

   # Backup targets. They will be processed in order.
   #
   # Details on the config values should be documented in the target modules
   TARGETS = [
      dict(
         name = "local",
         profile = "folder",
         config = dict(
            # retention: how long is old data kept. The value is used as keyword
            # arguments dict for datetime.timedelta
            retention = timedelta(days=7),
            path = THE_BACKUP_DIR,
            ),
         ),
      dict(
         name = "rsync",
         profile = "rsync",
         config = dict(
            ssh_key = "%s/id_dsa" % THE_BACKUP_DIR,
            )
         ),
      dict(
         name = "ftp",
         profile = "ftp",
         config = dict(
            host="my.ftp.host",
            username="ftpuser",
            password="asis! Light!",
            remote_folder="backups",
            retention = timedelta(days=20),
            )
         ),
   ]


.. _advanced_config:

As the config file is a python script, you can do pretty much everything you
want with it. What this will show you:

   - Use of comments (Lines starting with ``#``)

   - Usage of python modules from the standard library (in this case:
     ``timedelta``, ``os.path``, ``os``)

   - using the ``dict()`` notation instead of ``{}`` literals. I personally
     find this a lot more comfortable to write and read. But other than that,
     both options are identical.

   - programatically adding entries to the ``GENERATORS`` list.

     This script will, at each execution, look for folders containing a file
     ``do_backup`` under an example "projects" folder. If it fines one, that
     folder is added to the generators.

     As you can see, the config files can
     become arbitrarily complex.

Advanced config file::

   import os
   import os.path

   # Config version (major, minor)
   CONFIG_VERSION = (2,1)

   # Use the first target profile as staging area
   FIRST_TARGET_IS_STAGING

   # A custom variable. Not used by the application itself, but used here, in
   # the config script!
   THE_BACKUP_DIR = "/var/backups/data"

   # All backups will be created in this folder before being deployed to the
   # targets
   STAGING_AREA = "staging"

   # Backup Sources. They will be processed in order
   #
   # Details on the config values should be documented in the source modules
   GENERATORS = [
      dict(
         name = 'MySQL',
         profile = 'mysql',
         config = dict(
            # user should have full priviledges on everything
            database = '*',
            port = "3306",
            host = "localhost",
            user = "root",
            password = "mysecretpassword"
            ),
         ),
      dict(
         name = 'PostgreSQL 8.4',
         profile = 'postgres',
         config = dict(
            host = 'localhost',
            database = 'killerdb',
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
         name = '/var/mail',
         profile = 'folder',
         config = dict(
            path = '/var/mail',
            )
         ),
      ]

   #
   # Append each folder inside "/path/with/projects" which also contains a
   # "special" file "do_backup"
   #
   projects_root = "/path/with/projects"
   for entry in os.listdir(projects_root):
      trigger_filename = "do_backup"
      entrypath = os.path.abspath(
         os.path.join(projects_root, entry))

      if not os.path.isdir(entrypath):
         # This entry is not a folder. So we'll skip it
         continue

      if not os.path.exists(os.path.join(entrypath, trigger_filename)):
         # This folder does not contain a file named "do_backup"
         # We'll skip this too.
         continue

      # Everything remaining is a directory containing "do_backup"
      # Let's add it to the GENERATORS list.
      GENERATORS.append(dict(
            name = 'Project folder: %s' % entrypath,
            profile = 'folder',
            config = dict(
               path = entrypath,
               )
            ))

   #
   # Backup targets. They will be processed in order.
   #
   TARGETS = [
      dict(
         name = "local",
         profile = "dailyfolder",
         config = dict(
            retention = dict( days=7 ),
            path = THE_BACKUP_DIR,
            ),
         ),
      dict(
         name = "ftp",
         profile = "ftp",
         config = dict(
            host="my.ftp.host",
            username="ftpuser",
            password="asis! Light!",
            remote_folder="backups",
            retention = dict(weeks=52),
            )
         ),
   ]



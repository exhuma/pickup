"""
This module will dump the databases running ``pg_dump`. The output will be run
through ``bzip2``.

Prerequisites
~~~~~~~~~~~~~

   - ``psycopg2`` must be installed

Configuration
~~~~~~~~~~~~~

The following fields are used by this plugin:

   **host**
      The host on which the database is running

   **port**
      The port on which the database is running

   **database**
      The database to backup. This can be ``'*'`` to backup all databases
      (excluding ``template0``, ``template1`` and ``postgres``)

      .. note:: In order for the wildcard ``"*"`` to work in the config file,
                the user must be able to connect to "template1" and must have
                read access to the system table "pg_database".

A note on passwords
~~~~~~~~~~~~~~~~~~~

Unfortunately, there are problems with the way pg_dump prompts for passwords.
So connecting automatically is best possible using the available postgres
methods. The easiest to set up while being more secure than simple ``trust``
connections is the ``.~/pgpass`` file.

.. warning:: It's not recommended to use "trust" connections. For example,
          assume the following conditions are met:

            - A user has shell access
            - The ``pg_hba.conf`` file allows trust connections for the user
              postgres on local connections (a common setup).

          Then all the user needs to do is run the following command::

             $ psql -U postgres <dbname>

          to get access to the system! Using a ~/.pgpass file allows for
          convenient passwordless connections (as used by this script), while
          being a lot more secure than trust connections. Just keep in mind to
          set a chmod 600 on that file!

Here's a copy of the relevant docs:

   The file ``.pgpass`` in a user's home directory is a file that can contain
   passwords to be used if the connection requires a password (and no password
   has been specified otherwise). This file should have lines of the following
   format::

      hostname:port:database:username:password

   Each of the first four fields may be a literal value, or ``*``, which
   matches anything. The password field from the first line that matches the
   current connection parameters will be used. (Therefore, put more-specific
   entries first when you are using wildcards.) If an entry needs to contain
   ``:`` or ``\``, escape this character with ``\``.
"""

import logging
import psycopg2
from subprocess import Popen, PIPE
from os.path import join, exists, abspath
import os

LOG = logging.getLogger(__name__)
API_VERSION = (1,0)
MODULE_NAME = __name__.split(".")[-1]
CONFIG = {}
SOURCE = {}

def init(source):
   CONFIG.update(source['config'])
   SOURCE.update(source)
   LOG.debug("Initialised '%s' with %r" % ( __name__, CONFIG))

def list_dbs():
   conn = psycopg2.connect(
         database = 'template1',
         host = CONFIG['host'],
         port = CONFIG['port'],
      )
   cursor = conn.cursor()
   cursor.execute("SELECT datname FROM pg_database WHERE datname NOT IN "
         "('template0', 'template1', 'postgres')")
   output = [row[0] for row in cursor.fetchall()]
   cursor.close()
   conn.close()
   return output

def dump_one_db(staging_area, dbname):
   LOG.info("Dumping %s" % dbname)
   command = [
      'pg_dump',
      '-w',
      '-Ft',
      dbname ]

   target_folder = join(staging_area, MODULE_NAME)
   if not exists(target_folder):
      os.makedirs(target_folder)
      LOG.info("%s created" % abspath(target_folder))

   p1 = Popen( command, stdout=PIPE, stderr=PIPE )
   p2 = Popen( "bzip2", stdin=p1.stdout, stdout=open(
      join(target_folder, "%s.tar.bz2" % dbname), "wb"), stderr=PIPE )

   p2.wait()

   if p1.poll() != 0:
      LOG.error("Error while running pg_dump: %s" % p1.stderr.read())

   if p2.poll() != 0:
      LOG.error("Error while running bzip2: %s" % p2.stderr.read())

def run(staging_area):

   if CONFIG['database'] == '*':
      for dbname in list_dbs():
         dump_one_db(staging_area, dbname)
   else:
      dump_one_db(staging_area, CONFIG['database'])


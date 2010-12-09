"""
This module will dump the databases running ``pg_dump``. The output will be run
through ``bzip2``.

Prerequisites
~~~~~~~~~~~~~

   - ``psycopg2`` must be installed

Configuration
~~~~~~~~~~~~~

The following fields are used by this plugin:

   **host**
      The host on which the database is running

   **user**
      The username as whom to connect.

   **port**
      The port on which the database is running

   **database**
      The database to backup. This can be ``'*'`` to backup all databases
      (excluding ``template0``, ``template1`` and ``postgres``)

      .. note:: In order for the wildcard ``"*"`` to work in the config file,
                the user must be able to connect to "template1" and must have
                read access to the system table "pg_database".

   **pg_dump_params** (string) *optional*
      These parameters are passed directly to ``pg_dump``.

      .. warning:: The parameters for host, user and port (``-h``, ``-U``,
                   ``-p`` respectively) should be **avoided**! The plugin uses
                   the settings ``host``, ``user`` and ``port`` to set these
                   automatically.

                   The plugin uses two
                   types of connection: A programmatic connection using
                   ``libpq`` and indirect connection using the ``pg_dump`` and
                   ``pg_dumpall`` executables. The params specified in this
                   config variable will **only** be passed to ``pg_dump`` and
                   ``pg_dumpall``. So if you specify other host/user/port
                   variables as specified in the dedicated config variables
                   this may have unexpected results.

                   Additionally, the parameter ``-w`` (never prompt for
                   password) is automatically added. See the section
                   :ref:`postgres_passwords` for more info.

   **pg_dumpall_params** (string) *optional*
      Same as ``pg_dump_params``, but for the command ``pg_dumpall``

Configuration Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   dict(
      name = 'PostgreSQL 8.4',
      profile = 'postgres',
      config = dict(
         host = 'localhost',
         user = 'backup',
         database = '*', # using '*' will dump all dbs
         port = 5432,
         pg_dump_params = "-Ft -c",
         ),
      ),

.. _postgres_passwords:

A note on passwords
~~~~~~~~~~~~~~~~~~~

As a security precaution login credentials should be stored in "~/.pgpass".
Setting up "trust" connections works as well, but is far less secure!

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
import shlex
from subprocess import Popen, PIPE
from os.path import join, exists, abspath

LOG = logging.getLogger(__name__)
API_VERSION = (2,0)
CONFIG = {}
SOURCE = {}

def init(source):
   CONFIG.update(source['config'])
   SOURCE.update(source)
   LOG.debug("Initialised '%s' with %r" % ( __name__, CONFIG))

def list_dbs():
   conn = psycopg2.connect(
         database = 'template1',
         user = CONFIG['user'],
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

def get_params(command):
   """
   Construct a list of command-line params and return it.
   To be used in ``pg_dump`` and ``pg_dumpall``

   @param command: The command name (either "pg_dumpall" or "pg_dump")
   """
   key = "%s_params" % command
   out = []
   if "port" in CONFIG and CONFIG['port']:
      out.extend([ "-p", str(CONFIG['port']) ])
   if "host" in CONFIG and CONFIG['host']:
      out.extend([ "-h", CONFIG['host'] ])
   if "user" in CONFIG and CONFIG['user']:
      out.extend([ "-U", CONFIG['user'] ])
   if key in CONFIG and CONFIG[key]:
      out.extend( shlex.split(CONFIG[key]) )
   return out

def dump_one_db(staging_area, dbname):
   LOG.info("Dumping %s" % dbname)
   command = [ 'pg_dump', '-w' ]
   command.extend( get_params("pg_dump") )
   command.append( dbname )

   p1 = Popen( command, stdout=PIPE, stderr=PIPE )
   p2 = Popen( "bzip2", stdin=p1.stdout, stdout=open(
      join(staging_area, "%s.bz2" % dbname), "wb"), stderr=PIPE )

   p1.wait()
   p2.wait()

   if p1.returncode != 0:
      LOG.error("Error while running pg_dump: %s" % p1.stderr.read())

   if p2.returncode != 0:
      LOG.error("Error while running bzip2: %s" % p2.stderr.read())

def dump_globals(staging_area):
   LOG.info("Dumping posgtres globals")
   command = [ 'pg_dumpall', '-g' ]
   command.extend( get_params("pg_dumpall") )

   p1 = Popen( command, stdout=PIPE, stderr=PIPE )
   p2 = Popen( "bzip2", stdin=p1.stdout, stdout=open(
      join(staging_area, "globals.bz2" ), "wb"), stderr=PIPE )

   p1.wait()
   p2.wait()

   if p1.returncode != 0:
      LOG.error("Error while running pg_dump: %s" % p1.stderr.read())

   if p2.returncode != 0:
      LOG.error("Error while running bzip2: %s" % p2.stderr.read())

def run(staging_area):

   dump_globals(staging_area)
   if CONFIG['database'] == '*':
      for dbname in list_dbs():
         dump_one_db(staging_area, dbname)
   else:
      dump_one_db(staging_area, CONFIG['database'])


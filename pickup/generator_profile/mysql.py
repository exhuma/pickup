"""
This module will dump MySQL databases running ``mysqldump``. The output will be
run through ``bzip2``.

Prerequisites
~~~~~~~~~~~~~

   - ``mysql-python`` must be installed (``apt-get install python-mysqldb``)

Configuration
~~~~~~~~~~~~~

The following fields are used by this plugin:

   **database** (string)
      The database to backup. This can be ``'*'`` to backup all databases
      (excluding ``information_schema``)

      .. note:: In order for the wildcard ``"*"`` to work in the config file,
                the user must be able to connect to "mysql" and must have
                read access to the table "db".

   **host** (string) *optional* (default="localhost")
      The host on which the database is running

   **user** (string) *optional* (default="root")
      The user used to connect to the DB

   **password** (string) *optional* (default="")
      The password used to connect to the DB

   **port** (string/int) *optional* (default=3306)
      The port on which the database is running

   **mysqldump_params** (string) *optional*
      These parameters are passed directly to ``mysqldump``.

      .. warning:: The parameters for host, user, port and password (``-h``,
                   ``-u``, ``-p`` and ``-P`` respectively) should be
                   **avoided**! The plugin uses the settings ``host``, ``user``
                   and ``port`` to set these automatically.

                   The plugin uses two types of connection: A programmatic
                   connection using ``libmysql`` and indirect connection using
                   the ``mysqldump`` executables. The params specified in this
                   config variable will **only** be passed to ``mysqldump``. So
                   if you specify other host/user/password/port variables as
                   specified in the dedicated config variables this may have
                   unexpected results.

Configuration Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   dict(
      name = 'MySQL',
      profile = 'mysql',
      config = dict(
         database = "*",
         port = "3306",
         host = "localhost",
         user = "backupuser",
         password = "foobar"
         mysqldump_params = "",
         connection_params = dict(
            charset='utf8',
            compress=True
         )
      ),
   ),

"""
import logging
import shlex
import MySQLdb
from subprocess import Popen, PIPE
from os.path import join
LOG = logging.getLogger(__name__)
API_VERSION = (2,0)
CONFIG = {}

def init(source_dict):
   LOG.debug("Hello, I was initialised with %s" % source_dict)
   CONFIG.update(source_dict["config"])

def dump_all_dbs(conn, staging_area):
   # get a list of all available dbs
   cur = conn.cursor()
   cur.execute("SHOW databases")
   for row in cur.fetchall():
      # Database "mysql" is *always* included in the backup. It contains
      # critical data like usernames and passwords. Without it a backup is
      # worthless. So we ignore it here, and create it separately in the main
      # "run" method.
      if row[0] not in ["information_schema", "mysql"]:
         dump_one_db(conn, row[0], staging_area)
   cur.close()

def dump_one_db(conn, db, staging_area):
   LOG.info("Dumping %s" % db)

   command = [ 'mysqldump',
      "-P", str(CONFIG.get('port', 3306)),
      "-h", CONFIG.get('host', "localhost"),
      "-u", CONFIG.get('user', "user"),
      "-p%s" % CONFIG.get('password', "") ]

   if "mysqldump_params" in CONFIG and CONFIG["mysqldump_params"]:
      command.extend( shlex.split(CONFIG["mysqldump_params"]) )
   command.append( db )
   LOG.debug("Running command %r" % command)

   p1 = Popen( command, stdout=PIPE, stderr=PIPE )
   p2 = Popen( "bzip2", stdin=p1.stdout, stdout=open(
      join(staging_area, "%s.bz2" % db), "wb"), stderr=PIPE )

   p1.wait()
   p2.wait()

   if p1.returncode != 0:
      LOG.error("Error while running mysql_dump: %s" % p1.stderr.read())

   if p2.returncode != 0:
      LOG.error("Error while running bzip2: %s" % p2.stderr.read())

def run(staging_area):

   # so far so good. connect...
   conn = MySQLdb.connect( db="mysql",
        user = CONFIG.get("user", "root"),
        passwd = CONFIG.get('password', ""),
        host = CONFIG.get('host', "localhost"),
        port = CONFIG.get('port', 3306),
        **CONFIG.get('connection_params', {})
        )

   # always create a backup of "mysql" if possible
   dump_one_db(conn, "mysql", staging_area)
   if CONFIG['database'] == '*':
      dump_all_dbs(conn, staging_area)
   else:
      dump_one_db(conn, CONFIG['database'], staging_area)

   conn.close()


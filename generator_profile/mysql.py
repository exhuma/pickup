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

   **host** (string) *optional*
      The host on which the database is running

   **port** (string/int) *optional*
      The port on which the database is running

   **mysqldump_params** (string) *optional*
      These parameters are passed directly to ``mysqldump``.

      .. warning:: The parameters for host, user and port (``-h``, ``-u``,
                   ``-p`` respectively) should be **avoided**! The plugin uses
                   the settings ``host``, ``user`` and ``port`` to set these
                   automatically.

                   The plugin uses two types of connection: A programmatic
                   connection using ``libmysql`` and indirect connection using
                   the ``mysqldump`` executables. The params specified in this
                   config variable will **only** be passed to ``mysqldump``. So
                   if you specify other host/user/port variables as specified
                   in the dedicated config variables this may have unexpected
                   results.

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
         mysqldump_params = "",
         ),
      ),

.. _mysql_passwords:

A note on passwords
~~~~~~~~~~~~~~~~~~~

As a security precaution login credentials should be stored in "~/.my.cnf".
Setting up passwordless connections should work as well, but is far less
secure!

Read `the MySQL docs
<http://dev.mysql.com/doc/refman/5.1/en/option-files.html>`_ for more on this
subject.

An example ``~/.my.cnf`` could look like this::

    [client]
    user = backup
    password = the.super-s3cr1t

"""
import logging
import MySQLdb
from subprocess import Popen, PIPE
from os.path import join, exists, expanduser
LOG = logging.getLogger(__name__)
API_VERSION = (1,0)
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

   command = [ 'mysqldump' ]
   if "port" in CONFIG and CONFIG['port']:
      command.extend([ "-P", str(CONFIG['port']) ])
   if "host" in CONFIG and CONFIG['host']:
      command.extend([ "-h", CONFIG['host'] ])
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

   # use ~/.my.cnf for login/password data
   mysql_option_file = expanduser("~/.my.cnf")
   if not exists(mysql_option_file):
      LOG.error("~/.my.cnf does not exist! Execution halted! "
            "See the documentation for more information!")
      return

   # so far so good. connect...
   conn = MySQLdb.connect( db="mysql",
         read_default_file=mysql_option_file )

   # always create a backup of "mysql" if possible
   dump_one_db(conn, "mysql", staging_area)
   if CONFIG['database'] == '*':
      dump_all_dbs(conn, staging_area)
   else:
      dump_one_db(conn, CONFIG['database'], staging_area)

   conn.close()


#!/usr/bin/python
"""
The remote_tar plugin runs a tar command on a remote host and retrieves the
generated tar file. In this initial version, the details are specified in the
config variable "tar_params".

Configuration
~~~~~~~~~~~~~

The following fields are used by this plugin:

   **username** (string)
      The username to connect as to the remote host

   **hostname** (string)
      The hostname to connect to.

   **tar_params** (string)
      The parameters passed to the tar command (f.ex.: ``-cz /path/to/files``)

      .. warning:: Do not specify a target filename with the ``-f`` parameter!
                   This plugin uses ``mktemp`` to create a file as securely and
                   uniquely as possible! On the other hand, when using the
                   ``-f`` parameter, this plugin will not know which file to
                   transfer over! Use the config option "target_filename"
                   instead!

   **target_filename** (string)
      The **local** filename (that is: The filename that is created inside the
      staging area)

   **port** (int) *optional*
      The port to connect to (default=22)

   **password** (string) *optional*
      The password for the user. (default=None)

      .. note:: Leave this empty if you want to use privat/public key
                authentication (see: "key_filename")

   **key_filename** (string|list of strings) *optional*
      A filename (or list of filenames) which is/are used as private/public key
      authentication.

      .. note:: Leave this empty if you want to use password authentication
                (see: "password")

   **tmpfolder** (string) *optional*
      A folder on the **remote** machine! If this is left empty, the default
      system location is used (usually ``/tmp``).

      .. warning:: Leaving this empty *may* be a potential security risk as
                   everybody has read access to ``/tmp``! This value is used
                   with ``mktemp``.  ``mktemp`` usually creates files with mode
                   ``0600`` so this is less of a concern. It may be useful,
                   where this is not ensured.

Configuration Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   dict(
      name = 'My home folder',
      profile = 'remote_tar',
      config = dict(
         username = 'ninjamonkey',
         hostname = 'batcave',
         port = 64222,
         key_filename = ["/home/ninjamonkey/ssh_keys/batcave.rsa"],
         tmpfolder = "",
         tar_params = "-cz /home/ninjamonkey",
         target_filename = "home_ninjamonkey.tar.gz"
         )
      ),
"""

import paramiko
import logging
from os.path import join

LOG = logging.getLogger(__name__)
API_VERSION = (2,0)
CONFIG = {}
SOURCE = {}

def init(source):
   CONFIG.update(source['config'])
   SOURCE.update(source)
   LOG.debug("Initialised '%s' with %r" % ( __name__, CONFIG))

def connect():
   client = paramiko.SSHClient()
   client.load_system_host_keys()
   client.set_missing_host_key_policy(paramiko.WarningPolicy())

   LOG.info("Connecting to remote host %r" % CONFIG['hostname'])
   client.connect(
         hostname = CONFIG['hostname'],
         port = CONFIG.get('port', 22),
         username = CONFIG['username'],
         password = CONFIG.get('password', None),
         key_filename = CONFIG.get('key_filename', None)
         )
   return client

def exec_ssh(client, command):
   LOG.info("Executing remote command %r" % command)
   _, stdout, stderr = client.exec_command(command)
   stdout = stdout.read().strip()
   stderr = stderr.read().strip()
   LOG.debug("Remote STDOUT")
   LOG.debug(stdout)

   if stderr:
      LOG.error("Remote STDERR")
      LOG.error(stderr)

   return stdout, stderr

def cleanup(client, tar_name):
   LOG.debug( "Removing %r on remote site % tar_name" )
   exec_ssh(client, "rm -v %s" % tar_name)
   client.close()

def create_tar(client):
   # create a temporary file
   stdout, stderr = exec_ssh(client, "mktemp --tmpdir=%s" % CONFIG.get("tmpfolder", ""))
   tmpfile = stdout
   LOG.debug("Remote temp file: %r" % tmpfile)

   if not tmpfile:
      raise ValueError("No tempfile name received. Cannot continue!")

   # create the tar file
   exec_ssh(client, "tar %s > %s" % (CONFIG['tar_params'], tmpfile))
   return tmpfile

def download_tar(client, tar_name, target_folder):
   LOG.info("Downloading %r into %r" % (tar_name, target_folder))
   sftp = client.open_sftp()
   sftp.get( tar_name, join(target_folder, CONFIG["target_filename"]) )
   sftp.close()

def run(staging_area):
   if not "target_filename" in CONFIG:
      LOG.error("Config key 'target_filename' is required!")
      return

   if not "tar_params" in CONFIG:
      LOG.error("Config key 'tar_params' is required!")

   client = connect()
   tar_name = create_tar(client)
   download_tar(client, tar_name, staging_area)
   cleanup(client, tar_name)

if __name__ == "__main__":
   logging.basicConfig(level=logging.INFO)
   logging.getLogger("paramiko.transport.sftp").setLevel(logging.DEBUG)
   run(".")


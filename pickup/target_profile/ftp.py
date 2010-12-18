"""
Uploads the staging folder to an FTP host. On the remote host a new subfolder
with the current date will be created (f.ex.: '2010-11-01'). The staging area
will be stored in that folder.

Configuration
~~~~~~~~~~~~~

The following fields are used by this plugin:

   **host** (string)
      The FTP hostname

   **username** (string)
      The username

   **password** (string)
      The password for the user

   **remote_folder** (string) *optional*
      If specified, the backups will be rooted in this folder. If not
      specified, the backups will be created on the default folder.

   **retention** (dict) *optional*
      How long the data should be kept. Everything older than this will be
      deleted. The dictionary values will be passed as keyword arguments to
      `datetime.timedelta
      <http://docs.python.org/library/datetime.html#datetime.timedelta>`_. If
      set to ``None``, the data will be kept indefinitely!

      **Default:** ``None``

      .. note:: This script uses the folder name to determine the date! All
                folders that have a name not expected by this script, will
                issue a warning.

   **dry_run** (boolean) *optional*
      If set to ``True`` no files will be uploaded or deleted. Instead, the
      operations will only be reported to stdout.

      .. note:: Folders will still be created on the remote host to have an
                accurate simulation.

Configuration Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   dict(
      name = "my ftp host",
      profile = "ftp",
      config = dict(
         host="ftp.myhost.net",
         username="itsame",
         password="maario",
         dry_run=True,
         remote_folder="tube/coins",
         retention=dict(
               weeks=52
            ),
         )
      ),

"""

from datetime import datetime, timedelta
import logging
import os
import os.path
from ftplib import FTP, error_perm

LOG = logging.getLogger(__name__)
API_VERSION = (2,0)
CONFIG = {}
FOLDER_FORMAT = "%Y-%m-%d"

def init(target):
   CONFIG.update(target['config'])
   LOG.debug("Initialised '%s' with %r" % ( __name__, CONFIG))

def try_mkd( conn, foldername ):
   try:
      conn.mkd(foldername)
   except Exception, e:
      if "File exists" in str(e):
         pass
      else:
         raise

def folder():
   return

def rmrf(conn, path):
   LOG.debug('Recursively deleting %s' % path)
   conn.cwd(path)
   for entry in conn.nlst():
      if entry in (".", ".."):
         continue

      try:
         conn.delete(entry)
      except error_perm, exc:
         # Permission Denied (most likely a directory)
         try:
            rmrf(conn, entry)
         except Exception, exc2:
            # Probably not a directory. Skip this entry
            LOG.warning(str(exc2))
            pass
   conn.cwd("..")
   conn.rmd(path)

def remove_old_files(conn, timedelta_params):
   delta = timedelta(**timedelta_params)
   threshold_date = datetime.now() - delta
   LOG.info("Removing files created before %s" % threshold_date)
   for entry in conn.nlst():
      if entry in ('.', '..'):
         continue

      try:
         entry_date = datetime.strptime(entry, FOLDER_FORMAT)
         LOG.debug("Inspecting %s (threshold=%s, todelete=%s)" % (
            entry, threshold_date, entry_date<threshold_date ))
         if entry_date < threshold_date:
            LOG.info("Deleting %s" % entry)
            if not CONFIG.get("dry_run", False):
               rmrf(conn, entry)
      except ValueError, e:
         LOG.warning( str(e) )
   else:
      LOG.info("All obsolete files successfully removed.")

def run_ftp(staging_area):
   """
   Run the ftp profile

   I put this in a separate method to make error-handling and work-dir
   restoration easier to read in the "run" method.
   """
   os.chdir(staging_area)
   current_date_folder = datetime.now().strftime(FOLDER_FORMAT)

   ftp = FTP(CONFIG['host'],
         user=CONFIG['username'],
         passwd=CONFIG['password']
         )

   if CONFIG.get('remote_folder', None):
      try_mkd( ftp, CONFIG['remote_folder'] )
      ftp.cwd(CONFIG['remote_folder'])

   # delete old files
   timedelta_params = CONFIG.get('retention', None)
   if timedelta_params:
      remove_old_files(ftp, timedelta_params)

   try_mkd( ftp, current_date_folder )
   ftp.cwd( current_date_folder )

   backup_root = ftp.pwd()
   LOG.info("Current FTP folder: %r" % backup_root)

   for root, dirs, files in os.walk("."):
      ftp.cwd(backup_root)

      if root == '.':
         continue

      # create required folder structure
      for node in os.path.split(root):
         if node == '.':
            continue

         try_mkd(ftp, node)
         ftp.cwd(node)

      # upload files
      for filename in files:
         LOG.info( "Uploading %s to %s" % (
            filename, ftp.pwd()))
         if not CONFIG.get("dry_run", False):
            ftp.storbinary( "STOR %s" % filename,
                  open(os.path.join(root,filename), "rb") )

   ftp.quit()

def run(staging_area):
   workdir_bak = os.getcwd()

   try:
      run_ftp(staging_area)
   except Exception, e:
      LOG.exception(e)

   os.chdir(workdir_bak)



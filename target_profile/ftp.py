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
         remote_folder="tube/coins",
         )
      ),

"""

from datetime import datetime
import logging
import os
import os.path

LOG = logging.getLogger(__name__)
API_VERSION = (1,0)
CONFIG = {}

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

def run(staging_area):
   os.chdir(staging_area)
   current_date_folder = datetime.now().strftime("%Y-%m-%d")

   from ftplib import FTP
   ftp = FTP(CONFIG['host'],
         user=CONFIG['username'],
         passwd=CONFIG['password']
         )
   #ftp.retrlines('LIST')     # list directory contents
   if 'remote_folder' in CONFIG and CONFIG['remote_folder']:
      ftp.cwd(CONFIG['remote_folder'])

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
         ftp.storbinary( "STOR %s" % filename,
               open(os.path.join(root,filename), "rb") )

   ftp.quit()



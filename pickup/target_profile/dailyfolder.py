"""
Creates a subfolder with the current date (YYYY-MM-DD) in the target folder and
copies everything inside the staging area into that folder

Configuration
~~~~~~~~~~~~~

The following fields are used by this plugin:

   **path** (string)
      The target folder

   **retention** (dict) *optional*
      How long the data should be kept. Everything older than this will be
      deleted. The dictionary values will be passed as keyword arguments to
      `datetime.timedelta
      <http://docs.python.org/library/datetime.html#datetime.timedelta>`_. If
      set to ``None``, the data will be kept indefinitely!

      **Default:** ``None``

      .. note:: This script uses the OSs ``mtime`` value to determine the
                folder's date. Refer to you OS reference to see if this is what
                you want!

Configuration Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   dict(
      name = "local",
      profile = "folder",
      config = dict(
         path = "/var/backups",
         retention = dict(
               days=30,
               hours=12
            )
         ),
      ),

"""

from datetime import datetime, timedelta
from os.path import exists, join
from os import listdir, stat
from shutil import copytree, rmtree
import stat as stat_info
import logging
import os

LOG = logging.getLogger(__name__)
API_VERSION = (2,0)
CONFIG = {}
TARGET = {}

def init(target):
   CONFIG.update(target['config'])
   TARGET.update(target)
   LOG.debug("Initialised '%s' with %r" % ( __name__, CONFIG))

def folder():
   return join(CONFIG['path'], datetime.now().strftime('%Y-%m-%d'))

def remove_old_files(root, timedelta_params):
   delta = timedelta(**timedelta_params)
   threshold_date = datetime.now() - delta
   LOG.info("Removing files created before %s" % threshold_date)
   for entry in listdir(root):
      file_meta = stat(join(root, entry))
      mtime = datetime.fromtimestamp(file_meta[stat_info.ST_MTIME])
      LOG.debug("Inspecting %s (mtime=%s, threshold=%s, todelete=%s)" % (
         entry, mtime, threshold_date, mtime<threshold_date ))
      if mtime < threshold_date:
         LOG.info("Deleting %s" % entry)
         rmtree(join(root, entry))
   else:
      LOG.info("All obsolete files successfully removed.")

def run(staging_area):
   if not exists(CONFIG['path']):
      os.makedirs(CONFIG['path'])
      LOG.info("Path '%s' created." % CONFIG['path'])

   # delete old files
   timedelta_params = CONFIG.get('retention', None)
   if timedelta_params:
      remove_old_files(CONFIG['path'], timedelta_params)

   # store new files
   copytree(staging_area, folder())


"""
Creates a subfolder with the current data in the target folder and copies
everything inside the staging area into that folder

Configuration
~~~~~~~~~~~~~

The following fields are used by this plugin:

   **path**
      The target folder
"""

from datetime import datetime
from os.path import exists, join
from shutil import copytree
import logging
import os

LOG = logging.getLogger(__name__)
API_VERSION = (1,0)
CONFIG = {}
TARGET = {}

def init(target):
   CONFIG.update(target['config'])
   TARGET.update(target)
   LOG.debug("Initialised '%s' with %r" % ( __name__, CONFIG))

def run(staging_area):
   if not exists(CONFIG['path']):
      os.makedirs(CONFIG['path'])
      LOG.info("Path '%s' created." % CONFIG['path'])
   now = datetime.now()
   copytree(staging_area, join(CONFIG['path'], now.strftime('%Y-%m-%d')))


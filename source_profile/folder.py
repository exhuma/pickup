"""
The folder plugin create a bzipped tar file for a specific folder. It is also
possible to specify a parent folder and create individual tarballs for each
folder and one for files beneath that folder.

Configuration
~~~~~~~~~~~~~

The following fields are used by this plugin:

   **path** (string)
      The folder

   **split** (boolean) *optional*
      If set to "True", this module will create individual tarballs (Default =
      False).

"""
import logging
import tarfile
import re
from datetime import datetime
from os.path import exists, join, abspath, isdir, isfile
import os

LOG = logging.getLogger(__name__)
API_VERSION = (1,0)
CONFIG = {}
SOURCE = {}

def init(source):
   """
   If split is set, this strategy will create one folder per subfolder in the
   given path.
   """
   CONFIG.update(source['config'])
   SOURCE.update(source)
   LOG.debug("Initialised '%s' with %r" % ( __name__, CONFIG))

def run(staging_area):
   if not exists(CONFIG['path']):
      LOG.error("Path '%s' does not exist! Skipping!" % CONFIG['path'])
      return

   module_name = __name__.split(".")[-1]

   if CONFIG.get("split", False):
      create_split_tar(join(staging_area, module_name))
   else:
      create_simple_tar(join(staging_area, module_name))

def create_split_tar(staging_area):
   """
   Creates one tar file for each folder found in CONFIG['path']. If normal
   files reside in that folder, they will be collected into a special tarfile
   named "__PICKUP_FILES__.tar.bz2"

   @param staging_area: The target folder
   """

   if not isdir(CONFIG['path']):
      LOG.error("Impossible to create a split tar! %s is not a folder!" % CONFIG['path'])
      return

   # Create the "container" folder inside the staging area
   basename = get_basename()
   container = join(staging_area, basename)
   if not exists(container):
      os.makedirs( container )
   elif not isdir(container):
      LOG.error("'%s' exists and is not a folder! Skipping" % container)
      return

   files = []
   for entry in os.listdir(CONFIG['path']):
      entrypath = join(CONFIG['path'], entry)

      # Add directories directly, and add normal files into a special filename
      if not isdir(entrypath):
         files.append(entrypath)
         continue

      tarname = join(container, "%s.tar.bz2" % entry)
      LOG.info("Writing to '%s'" % abspath(tarname))
      tar = tarfile.open(abspath(tarname), "w:bz2")
      tar.add(entrypath)
      tar.close()

   if files:
      tarname = join(container, "__PICKUP_FILES__.tar.bz2")
      LOG.info("Writing remaining files to '%s'" % abspath(tarname))
      tar = tarfile.open(abspath(tarname), "w:bz2")
      for file in files:
         LOG.info("   Adding %s" % file)
         tar.add(file)
      tar.close()

def get_basename():
   # create the desired filename
   now = datetime.now()
   basename = "%s-%s" % (
         now.strftime("%Y-%m-%d"),
         re.sub( r'[^a-zA-Z0-9]', "_", SOURCE['name'] )
         )

   # prevent accidental overwrites
   counter = 0
   while exists(basename):
      counter += 1
      LOG.debug( "File %s exists. Adding a counter." % basename )
      basename = "%s-%d" % (basename, counter)
   return basename

def create_simple_tar(staging_area):
   tarname = "%s.tar.bz2" % get_basename()

   # put it into the staging area
   tarname = join(staging_area, tarname)

   LOG.info("Writing to '%s'" % abspath(tarname))
   tar = tarfile.open(abspath(tarname), "w:bz2")
   tar.add( CONFIG['path'] )
   tar.close()

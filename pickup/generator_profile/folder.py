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

Configuration Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   dict(
      name = 'My home folder',
      profile = 'folder',
      config = dict(
         path = '/home/me',
         split = True,
         )
      ),
"""
import logging
import tarfile
import re
from os.path import exists, join, abspath, isdir
import os

LOG = logging.getLogger(__name__)
API_VERSION = (2,0)
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

   if CONFIG.get("split", False):
      create_split_tar(staging_area)
   else:
      create_simple_tar(staging_area)

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

   LOG.info("Creating tarball for each folder inside %s" % CONFIG['path'])
   if not exists(staging_area):
      os.makedirs( staging_area )
   elif not isdir(staging_area):
      LOG.error("'%s' exists and is not a folder! Skipping" % staging_area)
      return

   files = []
   for entry in os.listdir(CONFIG['path']):
      entrypath = join(CONFIG['path'], entry)

      # Add directories directly, and add normal files into a special filename
      if not isdir(entrypath):
         files.append(entrypath)
         continue

      tarname = join(staging_area, "%s.tar.bz2" % entry)
      LOG.info("Writing to '%s'" % abspath(tarname))
      tar = tarfile.open(abspath(tarname), "w:bz2")
      tar.add(entrypath)
      tar.close()

   if files:
      tarname = join(staging_area, "__PICKUP_FILES__.tar.bz2")
      LOG.info("Writing remaining files to '%s'" % abspath(tarname))
      tar = tarfile.open(abspath(tarname), "w:bz2")
      for file in files:
         LOG.info("   Adding %s" % file)
         tar.add(file)
      tar.close()

def get_basename():
   """
   Create a 'clean' filename
   """

   # replace non-ascii characters with underscores
   basename = re.sub( r'[^a-zA-Z0-9]', "_", SOURCE['name'] )

   # now remove all leading/trainling underscores
   basename = basename.strip("_")

   # prevent accidental overwrites
   counter = 0
   while exists(basename):
      counter += 1
      LOG.debug( "File %s exists. Adding a counter." % basename )
      basename = "%s-%d" % (basename, counter)
   return basename

def create_simple_tar(staging_area):
   LOG.info("Creating tarball for path %s" % CONFIG['path'])
   tarname = "%s.tar.bz2" % get_basename()

   # put it into the staging area
   tarname = join(staging_area, tarname)

   LOG.info("Writing to '%s'" % abspath(tarname))
   tar = tarfile.open(abspath(tarname), "w:bz2")
   tar.add( CONFIG['path'] )
   tar.close()

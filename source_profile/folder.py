import logging
import tarfile
import re
from datetime import datetime
from os.path import exists, join, abspath

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

   # create the desired filename
   now = datetime.now()
   tarname = "%s-%s" % (
         now.strftime("%Y-%m-%d"),
         re.sub( r'[^a-zA-Z0-9]', "_", SOURCE['name'] )
         )

   # prevent accidental overwrites
   counter = 0
   while exists(tarname):
      counter += 1
      LOG.debug( "File %s exists. Adding a counter." % tarname )
      tarname = "%s-%d" % (tarname, counter)
   tarname += ".tar.bz2"

   # put it into the staging area
   tarname = join(staging_area, tarname)

   LOG.info("Writing to '%s'" % abspath(tarname))
   tar = tarfile.open(abspath(tarname), "w:bz2")
   tar.add( CONFIG['path'] )
   tar.close()

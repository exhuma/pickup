import logging
LOG = logging.getLogger(__name__)
API_VERSION=(1,0)

def init(**kwargs):
   LOG.debug("Initialised with %r" % kwargs)

def process():
   print "Hello Folder"

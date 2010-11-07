#!/usr/bin/python
#
# This is a backup utility, archiving mysql, postgres, mail and web-data
# Copyright (C) 2010 Michel Albert
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
#
#-----------------------------------------------------------------------------
#
# some "grep targets":
# TODO: Idea: Add post-processing handlers (f.ex.: to create md5sums/sfv files of all files
#
#-----------------------------------------------------------------------------

from datetime import datetime, timedelta
from os.path import exists, abspath
import os
import logging
import sys
LOG = logging.getLogger(__name__)

try:
   import config
except ImportError, exc:
   LOG.critical( "config.py was not found! "
         "This file is required. If you just made a clean checkout, have a "
         "look at config.py.dist for an example." )
   sys.exit(9)

from term import TerminalController
import source_profile
import target_profile

#-----------------------------------------------------------------------------

EXPECTED_CONFIG_VERSION = (1,0)
TERM = TerminalController()

class OnlyInfoFilter(logging.Filter):
   """
   Filter out messages *above* a specific level.
   """
   def filter( self, record ):
      if record.levelno <= logging.INFO:
         return True
      else:
         return False

def check_config():
   """
   Makes some sanity checks on the config file. And gives warnings/errors if
   important conditions are not met (config version too old, ...)
   """

   if not hasattr(config, "CONFIG_VERSION"):
      LOG.warning( "The config file does not specify CONFIG_VERSION! I will "
            "try to continue anyway, but this field is recommended to allow "
            "some internal tests to work. I will assume the value '(1,0)'!" )
      config.CONFIG_VERSION = (1, 0)

   major, minor = config.CONFIG_VERSION
   expected_major, expected_minor = EXPECTED_CONFIG_VERSION

   if major < expected_major:
      LOG.critical("The config system has undergone a major change! "
            "I cannot continue without an upgrade!")
      sys.exit(9)

   if minor < expected_minor:
      LOG.warning("The config system has undergone a minor change! "
            "It should work, but you still should review the docs!")

   if major == expected_major and minor == expected_minor:
      LOG.debug( "Config version OK!" )

   if not hasattr(config, "SOURCES"):
      LOG.critical("Variable 'SOURCES' not found in config!")
      sys.exit(9)

   if not config.SOURCES:
      LOG.critical("No sources defined (variable exists but is empty)!")
      sys.exit(9)

   if not hasattr(config, "TARGETS"):
      LOG.critical("Variable 'TARGETS' not found in config!")
      sys.exit(9)

   if not config.TARGETS:
      LOG.critical("No targets defined (variable exists but is empty)!")
      sys.exit(9)

def setup_logging():
   """
   Log everything below warning to stdout, and
       everything above warning to stderr (including warning)
   """

   # main loggers
   LOG.setLevel(logging.DEBUG)
   err_format = logging.Formatter(TERM.RED + "%(asctime)s | %(name)s | %(levelname)s | %(message)s" + TERM.NORMAL)
   out_format = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
   stdout_handler = logging.StreamHandler(sys.stdout)
   stdout_handler.setLevel(logging.DEBUG)
   stdout_handler.addFilter( OnlyInfoFilter() )
   stdout_handler.setFormatter(out_format)
   stderr_handler = logging.StreamHandler(sys.stderr)
   stderr_handler.setLevel(logging.WARNING)
   stderr_handler.setFormatter(err_format)
   LOG.addHandler(stdout_handler)
   LOG.addHandler(stderr_handler)

   # plugin loggers
   src_log = logging.getLogger("source_profile")
   src_log.setLevel(logging.DEBUG)
   src_log.addHandler(stdout_handler)
   src_log.addHandler(stderr_handler)

   tgt_log = logging.getLogger("target_profile")
   tgt_log.setLevel(logging.DEBUG)
   tgt_log.addHandler(stdout_handler)
   tgt_log.addHandler(stderr_handler)

def api_is_compatible(module, api_version):
   """
   Check if a plugin module is compatible with this version of the application.

   @param module: The module
   """

   if not hasattr(module, "API_VERSION"):
      LOG.error("Module '%s' does not specify an API version! Skipping!" %
            module.__name__)
      return False

   major, minor = module.API_VERSION
   expected_major, expected_minor = api_version
   if major != expected_major:
      LOG.error("Module '%s' is out of date (major API version "
            "number is %d, but it should be %s). Skipping!" %
            ( module.__name__, major, expected_major))
      return False

   if minor < expected_minor:
      LOG.warning("Module '%s' is out of date (minor API version "
            "number is %d, but it should be %s). Will continue anyway..." %
            ( module.__name__, minor, expected_minor))
   return True

def stage(source):
   """
   Stage the source into the staging area

   @param source: The source profile (from the config)
   """
   LOG.info( "Staging source %(name)s [%(profile)s]" % source )
   profile = None
   try:
      profile = source_profile.create( source["profile"] )
      if not api_is_compatible(profile, (1,0)):
         return

   except ImportError, exc:
      LOG.error( "Unable to instantiate source profile %s. "
            "Error message was: %s" % (source["profile"], exc) )
   if not profile:
      return

def push(target):
   """
   Push the staging area onto a target

   @param target: The target (from the config)
   """
   LOG.info("Pushing to '%(name)s' [%(profile)s]" % target )

def init():
   if not exists(config.STAGING_AREA):
      os.makedirs(config.STAGING_AREA)
      LOG.info("Staging folder '%s' created" % abspath(config.STAGING_AREA))
   if not os.path.isdir(config.STAGING_AREA):
      LOG.critical("Staging folder '%s' is not a folder!" % abspath(config.STAGING_AREA))
      sys.exit(9)
   LOG.info("Staging area is: %s" % abspath(config.STAGING_AREA))

def main():
   init()
   now = datetime.now()
   LOG.info("Fetching sources")
   for source in config.SOURCES:
      stage(source)

   LOG.info("Pushing to targets")
   for target in config.TARGETS:
      push(target)

if __name__ == "__main__":
   setup_logging()
   check_config()
   LOG.info("Backup session starting...")
   main()
   LOG.info("Backup session finished.")


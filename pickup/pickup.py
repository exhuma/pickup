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

from datetime import datetime
from logging.handlers import RotatingFileHandler
from optparse import OptionParser
from os.path import exists, abspath, join, dirname, expanduser
from shutil import rmtree
import logging
import os
import sys
import re

import generator_profile
import target_profile
import config
from lib.term import TerminalController

LOG = logging.getLogger(__name__)
OPTIONS = {}
ARGS = []
config_instance = None

#-----------------------------------------------------------------------------

EXPECTED_CONFIG_VERSION = (2,2)
TERM = TerminalController()

class ReverseLevelFilter(logging.Filter):
    """
    Filter out messages *above* a specific level. (In other words: log only
    messages *below* maxlevel)
    """

    def __init__(self, maxlevel, *args, **kwargs):
        logging.Filter.__init__(self, *args, **kwargs)
        self.maxlevel = maxlevel

    def filter( self, record ):
        if record.levelno <= self.maxlevel:
            return True
        else:
            return False

def check_config():
    """
    Makes some sanity checks on the config file. And gives warnings/errors if
    important conditions are not met (config version too old, ...)
    """

    if not config_instance:
        LOG.error("Failed to load the config!")
        sys.exit(9)

    if not hasattr(config_instance, "CONFIG_VERSION"):
        LOG.warning( "The config file does not specify CONFIG_VERSION! I will "
                "try to continue anyway, but this field is recommended to allow "
                "some internal tests to work. I will assume the value '(1,0)'!" )
        config_instance.CONFIG_VERSION = (1, 0)

    major, minor = config_instance.CONFIG_VERSION
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

    if not hasattr(config_instance, "GENERATORS"):
        LOG.critical("Variable 'GENERATORS' not found in config!")
        sys.exit(9)

    if not hasattr(config_instance, "TARGETS"):
        LOG.critical("Variable 'TARGETS' not found in config!")
        sys.exit(9)

def setup_logging():
    """
    Log everything below warning to stdout, and
         everything above warning to stderr (including warning)
    """

    # make sure all messages are propagated to the top-level logger
    LOG.setLevel(logging.DEBUG)
    err_format = logging.Formatter(TERM.RED + "%(asctime)s | %(name)s | %(levelname)s | %(message)s" + TERM.NORMAL)
    out_format = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")

    gen_log = logging.getLogger("pickup.generator_profile")
    tgt_log = logging.getLogger("pickup.target_profile")

    if not OPTIONS.quiet:
        stdout_handler = logging.StreamHandler(sys.stdout)

        if OPTIONS.debug:
            stdout_handler.setLevel(logging.DEBUG)
        else:
            stdout_handler.setLevel(logging.INFO)

        stdout_handler.addFilter( ReverseLevelFilter(logging.INFO) )
        stdout_handler.setFormatter(out_format)
        LOG.addHandler(stdout_handler)
        gen_log.addHandler(stdout_handler)
        tgt_log.addHandler(stdout_handler)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(err_format)

    if not exists("logs"):
        os.makedirs("logs")
        os.chmod("logs", 0700)

    LOG_FILE = join("logs", "pickup.log")
    debug_handler = RotatingFileHandler(LOG_FILE,
            maxBytes=100000, backupCount=5)

    if exists(LOG_FILE):
        os.chmod(LOG_FILE, 0600)

    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(out_format)

    LOG.addHandler(stderr_handler)
    LOG.addHandler(debug_handler)

    # plugin loggers
    gen_log.setLevel(logging.DEBUG)
    gen_log.addHandler(stderr_handler)
    gen_log.addHandler(debug_handler)

    tgt_log.setLevel(logging.DEBUG)
    tgt_log.addHandler(stderr_handler)
    tgt_log.addHandler(debug_handler)

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

def get_profile_folder(container, profile_config):
    """
    Create a unique foldername for a profile based on it's name
    """

    # replace non-ascii characters with underscores
    profile_folder = re.sub( r'[^a-zA-Z0-9_-]', '_', profile_config['name'] )

    # now remove all leading/trainling underscores
    profile_folder = profile_folder.strip("_")

    # prepend the container
    profile_folder = join(container, profile_folder)

    # prevent accidental overwrites
    counter = 0
    while exists(profile_folder):
        counter += 1
        LOG.debug( "File %s exists. Adding a counter." % profile_folder )
        profile_folder = "%s-%d" % (profile_folder, counter)
    return profile_folder

def load_profile(package, profile_config):
    LOG.debug("Loading profile '%(name)s' [%(profile)s]" % profile_config )

    profile = None
    try:
        profile = package.create(profile_config["profile"])
        if not api_is_compatible(profile, (2,0)):
            return
        profile.init(profile_config)
    except ImportError, exc:
        LOG.error( "Unable to instantiate target profile %s. "
                "Error message was: %s" % (profile_config["profile"], exc) )

    return profile

def run_profile(package, profile_config):
    """
    Run the generator/target profile

    @param package: The profile package
    @param profile_config: The profile settings (from the config)
    """

    LOG.info("Running '%(name)s' [%(profile)s]" % profile_config )

    profile = load_profile(package, profile_config)
    if not profile:
        return

    # create a subfolder for generator profiles
    if package.__name__ == "pickup.generator_profile":

        # first folder level is the module name. Append this to the staging area
        module_folder = profile.__name__.split(".")[-1]
        module_folder = join(config_instance.STAGING_AREA, module_folder)

        # into the module folder we put a folder based on the profile's name
        staging_folder = get_profile_folder(module_folder, profile_config)

        # just in case it does not exist, we'll create all required folders
        if not exists( staging_folder ):
            os.makedirs( staging_folder )
            LOG.debug( "Created directory %r" % staging_folder )
    else:
        staging_folder = config_instance.STAGING_AREA

    try:
        profile.run(staging_folder)
    except Exception, exc:
        LOG.error("Error staging '%s'. Error message: %s" %
                (profile_config['name'], exc))
        LOG.exception(exc)

def get_lock_file():
    """
    Returns a lock file.
    """
    if OPTIONS.pidfile:
        return expanduser(OPTIONS.pidfile)

    if os.name == 'posix':
        return '/var/run/pickup.pid'
    elif os.name == 'nt':
        lock_file = join(os.environ['APPDATA'], 'pickup', 'pickup.pid')
        os.makedirs(dirname(lock_file))
        return lock_file
    else:
        LOG.error('Unable to create the lock file on this OS (%r)' % os.name)
        sys.exit(9)

def acquire_lock():
    """
    This method is used to prevent multiple instances running at the same time.
    It creates a lock file containing the current PID (if available).

    If the file exists, the application will exit with an error.
    """

    lock_file = get_lock_file()
    if exists(lock_file):
        LOG.critical('Lock file %r exists already. Is the process still running? Exiting with error...' % lock_file)
        sys.exit(9)

    LOG.info('Creating lock file: %r' % lock_file)
    with open(lock_file, 'w') as fptr:
        fptr.write("%d" % os.getpid())

def release_lock():
    """
    Releases the process lock acquired via `acquire_lock`.
    """
    lock_file = get_lock_file()
    if exists(lock_file):
        LOG.info('Removing lock file %r' % lock_file)
        os.unlink(lock_file)
    else:
        LOG.warning('Lock file %r did not exist.' % lock_file)

def init():
    global OPTIONS, ARGS, config_instance

    OPTIONS, ARGS = parse_cmd_args()
    setup_logging()

    LOG.info("Backup session starting...")

    try:
        config_instance = config.create(OPTIONS.config)
    except ImportError, exc:
        LOG.critical( "Error loading the config module %r! "
                "This file is required. If you just made a clean checkout, have a "
                "look at config/config.py.dist for an example." % OPTIONS.config )
        LOG.exception(exc)
        sys.exit(9)

    check_config()

    first_target = None
    if (hasattr(config_instance, "FIRST_TARGET_IS_STAGING") and
            config_instance.FIRST_TARGET_IS_STAGING):
        first_target = config_instance.TARGETS.pop(0)
        if first_target.get("profile") not in ('dailyfolder',):
            LOG.error("When using the first target as staging, it must be a local folder!")
            sys.exit(9)

        # retrieve the folder where the module will put the files
        profile = load_profile(target_profile, first_target)
        if not profile.folder():
            LOG.error("The target %s cannot be used as staging area (it's not"
                    " returning a local folder path )" % profile.__name__)
        config_instance.STAGING_AREA = profile.folder()

    if not exists(config_instance.STAGING_AREA):
        os.makedirs(config_instance.STAGING_AREA)
        LOG.info("Staging folder '%s' created" % abspath(config_instance.STAGING_AREA))
    if not os.path.isdir(config_instance.STAGING_AREA):
        LOG.critical("Staging folder '%s' is not a folder!" % abspath(config_instance.STAGING_AREA))
        sys.exit(9)
    LOG.info("Staging area is: %s" % abspath(config_instance.STAGING_AREA))

def main():

    init()

    acquire_lock()

    now = datetime.now()
    LOG.info("Fetching from generators")
    for generator in config_instance.GENERATORS:
        run_profile(generator_profile, generator)

    LOG.info("Pushing to targets")
    for target in config_instance.TARGETS:
        run_profile(target_profile, target)

    if (not hasattr(config_instance, "FIRST_TARGET_IS_STAGING") or
            not config_instance.FIRST_TARGET_IS_STAGING):
        LOG.info("Deleting staging area")
        rmtree(config_instance.STAGING_AREA)

    release_lock()

    LOG.info("Backup session finished.")

def parse_cmd_args():
    parser = OptionParser()
    parser.add_option("-p", "--pid-file", dest="pidfile",
                            help=("Store the PID of the process in FILE. "
                                "Defaults to /var/run/pickup.pid (Posix) or "
                                "%APPDATA%/pickup/pickup.pid (Windows)"),
                            action="store", default=None,
                            metavar = "FILE")
    parser.add_option("-c", "--config", dest="config",
                            help="The config file to use",
                            action="store", default="config")
    parser.add_option("-d", "--debug", dest="debug",
                            help="enable debug messages on stdout",
                            action="store_true", default=False)
    parser.add_option("-q", "--quiet",
                            action="store_true", dest="quiet",
                            default=False,
                            help="Suppress stdout (stderr will still enabled)")

    return parser.parse_args()


if __name__ == "__main__":
    main()

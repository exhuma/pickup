"""
The command plugin executes a shell command. It will capture stdout and stderr
to stdout.txt and stderr.txt respectively.

.. note::
   Piping multiple commands together does not work due to the simple usage of
   Popen! If you want to do this it is recommended to write an intermediary
   shell script.

Configuration
~~~~~~~~~~~~~

The following fields are used by this plugin:

   **command** (string)
      The command

   **returncodes_ok** (string) *optional*
      A list of expected return codes. All return codes in this list are
      considered to indicate successful process termination. If a different
      return code is received, the plugin will issue an error message including
      the capture stderr text.
      Default: [0]

   **popen_params** (dict) *optional*
      This dictionary is passed directly as keyword parameters to `Popen <http://docs.python.org/library/subprocess.html#subprocess.Popen>`_
      The most interesting parameters may be ``cwd`` and ``env``.

      .. warning::
         If you specify ``stderr`` or ``stdout`` in this parameter, it will
         override the default redirection. Which means, that the default files
         in the staging area will not be created!

Configuration Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   dict(
      name = 'test command',
      profile = 'command',
      config = dict(
         command = "find .",
         returncodes_ok = 1,
         popen_params = { 'cwd': '/tmp' }
         ),
      ),

"""
import logging
from os.path import join
from subprocess import Popen, PIPE
import shlex

LOG = logging.getLogger(__name__)
API_VERSION = (2,0)
CONFIG = {}
SOURCE = {}

def init(source):
   """
   Initialise the plugin
   """
   CONFIG.update(source['config'])
   SOURCE.update(source)
   LOG.debug("Initialised '%s' with %r" % ( __name__, CONFIG))

def run(staging_area):

   LOG.info( "Capturing output of command %r" % CONFIG['command'] )
   LOG.debug( "   shlex.split result: %r" % shlex.split(CONFIG['command']) )
   stdout = open( join(staging_area, "stdout.txt"), "w+" )
   stderr = open( join(staging_area, "stderr.txt"), "w+" )
   popen_params = CONFIG.get( 'popen_params', {} )
   process = Popen( shlex.split( CONFIG['command']),
      stdout=stdout,
      stderr=stderr,
      **popen_params)
   retcode = process.wait()
   expected_codes = CONFIG.get("returncodes_ok", [0])
   if isinstance(expected_codes, int):
      expected_codes = [expected_codes]
   if retcode not in expected_codes:
      LOG.error( "Process terminated with non-expected return code: %r"
            % retcode )
      stderr.seek(0)
      LOG.error( "STDERR data:\n%s" % stderr.read() )
   stdout.close()
   stderr.close()




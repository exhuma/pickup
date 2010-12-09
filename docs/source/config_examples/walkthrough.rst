Let's construct a configuration file statement-by-statement.

.. code-block:: python

   CONFIG_VERSION = (2,1)

This tells pickup that this configuration script conforms to the version "2.1".
This is used to detect if pickup can "understand" the directives in this config
file. If the minor number differs, it usually means, that pickup is still able
to work with this config, but new optional features have been added. Pickup
will still continue to work, but issue a warning to make you aware of possible
new features.

If, on the other hand the major number differs, pickup will be unable to
understand this config script and will abort with a critical error message.

.. code-block:: python

   STAGING_AREA = "staging"

This is the temporary folder name for the backups. If, like in this case the
folder is relative, then it will be relative to the folder from which pickup
was executed. Not the folder where pickup is installed. If you want to be safe,
use an absolute foldername.

.. code-block:: python

   GENERATORS = [{
         'name': 'local home folders',
         'profile': 'folder',
         'config': {
            'path': '/home',
            'split': True,
            }}]

The ``GENERATORS`` list contains all the data "sources". In other words, it
contains all the modules which will generate backup data. These "profiles" will
be executed in the order as they appear in the list.

In this case, we will back-up data contained inside ``/home`` and for each
folder contained therein, we will create a separate tarball. For more
information, see :ref:`available_plugins`

.. code-block:: python

   TARGETS = [{
         'name': "local",
         'profile': "dailyfolder",
         'config': {
            'path': "/var/backups/daily",
            'retention': { 'days': 7 }
            }}]

The ``TARGETS`` list contains all the destinations in which the created backup
data should be distributed to. Again, the entries are process in the same order
as they appear in the list.

In this case, this will store the backups in a folder with the current date
inside a "container" folder (``/var/backups/daily``). Folders older than 7 days
will be deleted. See :ref:`available_plugins` for more information.

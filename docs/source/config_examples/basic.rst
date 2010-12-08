The following configuration script will create a backup of each local home
folder. Each folder will be stored as separate tarball::

   CONFIG_VERSION = (2,0)
   STAGING_AREA = "staging"
   GENERATORS = [{
         'name': 'local home folders',
         'profile': 'folder',
         'config': {
            'path': '/home',
            'split': True,
            }}]

   TARGETS = [{
         'name': "local",
         'profile': "dailyfolder",
         'config': {
            'path': "/var/backups/daily",
            }}]


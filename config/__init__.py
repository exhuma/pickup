def create(plugname):
   module = 'config.%s' % plugname
   __import__(module)
   return globals()[plugname]


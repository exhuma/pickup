def create(plugname):

   if plugname in globals():
      module = reload(globals()[plugname])
      return module

   module = 'generator_profile.%s' % plugname
   __import__(module)
   return globals()[plugname]

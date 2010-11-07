def create(plugname, **init_params):

   if plugname in globals():
      module = reload(globals()[plugname])
      if hasattr(plugname, "init"):
         plugname.init( **init_params )
      return module

   module = 'target_profile.%s' % plugname
   __import__(module)
   globals()[plugname].init(**init_params)
   return globals()[plugname]

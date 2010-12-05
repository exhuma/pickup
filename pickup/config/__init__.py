from os.path import expanduser, exists, dirname, basename
import sys

def create(filename):
   user_config = expanduser(filename)
   user_config_folder = dirname(filename)
   module_name = basename(filename).rsplit(".", 1)[0]

   if exists(filename):
      sys.path.append(user_config_folder)
      the_instance = __import__(module_name)
      return the_instance
   else:
      raise ImportError("File %r not found!" % filename)


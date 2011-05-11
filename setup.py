from setuptools import setup, find_packages
setup(
   name = "pickup",
   version = "1.4",
   packages = find_packages(),
   entry_points = { 'console_scripts': ['pickup = pickup.pickup:main'] },
   install_requires = [
      'paramiko',
      'mysql-python',
      'psycopg2',
      ],
   author = "Michel Albert",
   author_email = "michel@albert.lu",
   description = "Modular backup script",
   license = "BSD",
   keywords = "backup",
   url = "http://exhuma.github.com/pickup",
)

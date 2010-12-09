.. _logging:

Logging
=======

Pickup uses `the standard python logging module
<http://docs.python.org/library/logging.html>`_. While not *yet* possible, you
will be able to take control over how and where messages are logged eventually.

Current Configuration
---------------------

Currently, the configuration is hardcoded inside ``pickup.py`` with the
following settings.

Two handlers:

   - Console Handler

     Always writes messages *above* severity **INFO** to ``stderr``.
     **DEBUG** and **INFO** messages will be sent to ``stdout`` unless the
     command line flag ``-q`` is specified.

   - An auto-rotating file handler

     This handler always write **everything** to a file ``logs/pickup.log``.
     The path is relative to **the current working folder**. This means, if you
     run the script from a cronjob, the current working folder will be the home
     folder of the user which executes the script.

     For security reasons, the file is set to mode 0600 (only accessible by
     it's owner).

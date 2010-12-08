.. _how_and_why:

Why (History)
=============

   Why am I writing this script and why would you want to use it?

I needed a simple way to create backups of a couple of folders, a few MySQL and
PostgreSQL databases and store the created files on a remote FTP site. I
implemented this using a small bash script using ``ncftp`` to store them on the
FTP site.

`zmanda backup <http://www.zmanda.com/>`_ Seemed to be a bit too much at the
time.

Over time the script became more and more generalised. And as a result more and
more unreadable. After it started using bash arrays quite heavily the resulting
syntax really got on my nerves. Recently I needed to create backups in a
similar fashion on another server. And there the fun started. A couple of
problems:

   - One server used a standard debian PostgreSQL installation, the other
     didn't. But the script used a ``psql`` parameter (``--cluster``) which is
     only available on the default debian installation.

   - A couple of minor things did not work exactly the same way on both
     servers.

Additionally, the script had one major annoyance from the beginning:

``ncftp`` writes all server messages to ``stdout``. So, to see errors, I had to
refrain from redirecting ``ncftp``'s output to ``/dev/null``. But that in turn
meant that I received a cron-mail on each execution. Eventually, I redirected
the FTP output to ``/dev/null``. That way I only got cron-mails when something
else went wrong. But I had to check the FTP regularly to see if the backups
arrived correctly.

I always wanted to fix these issues, and add a couple more functionalities to
the script. But given the complexity it already had, I thought it be time to
rewrite it using a different scripting language. I've chosen Python as language
of choice. A couple of reasons:

   - It's the language I am currently most proficient in

   - It's available on pretty much any standard Linux installation (other
     choice could have been perl.)

   - It is very dynamic and let's me write a modular application easily.

   - The syntax is very concise!

Execution Concept
=================

The application works in two main steps:

   - Generate the backup data (DB dumps, archive generation, ...) inside a
     temporary "staging area"

     See :term:`generator`

   - "publish" the generated files to one or more targets.

     See :term:`target`

Usage
=====

The config file specifies what to backup (``GENERATORS``), and where to store
it (``TARGETS``). See :ref:`configuration` for more information on the general
configuration.

The generators and targets are defined in python module inside generator_profile and
target_profiles.  For a list of available generators and targets see
:ref:`available_plugins`

If something is missing the list of plugins, you can easily write a new plugin
with only minimal python knowledge. See :ref:`writing_plugins` for more
information.

Application output uses the default python logging module. All informational
messages are routed to stdout, and all errors/warnings are routed to stderr.
This is useful for cron jobs: redirecting stdout to /dev/null still lets
important messages through, so cron can take the appropriate steps (send
mails?)

Debugging messages are logged to a auto-rotating file inside the "logs"
directory. This provides some semi-persistent storage. If something went wrong
and you redirected stdout (or deleted the cron-mails), you still may find some
useful info in that file.

Rough Roadmap
=============

The main goal is to have a script which has all the features that I had in my
previous bash script. These features are:

  - **[DONE]** Folder backups (split and simple)

  - **[DONE]** Push to folder

  - **[DONE]** Backup PostgreSQL

  - **[DONE]** Docs

  - **[DONE]** Backup MySQL

  - **[DONE]** Push to FTP

  - **[DONE]** Remove old files in target "dailyfolder" (using the retention
    value)

  - **[DONE]** Remove old files in target "ftp" (using the retention value)

Additional items on the todo list
---------------------------------

  - Push to a remote host via SSH

  - Move logging configuration out of the code


.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   generator
      A generator is a plugin responsible to create a backup file.

   target
      A target is a location where the created backup files are stored. Each
      target is provided by a :term:`target profile <target_profile>`

   target_profile
      A target profile is a simple python script which will take files out of
      the :term:`staging area` and put it into a :term:`target`

   generator_profile
      A generator profile is a simple python script which will create files
      inside the :term:`staging area`. The primary use of a generator profile
      is to create files containing the backup data. But they could also create
      other files.

   staging area
      The staging area is nothing more than a temporary location. The files
      created by generators will be stored in this folder. Once all generators
      have finished, the target profiles will take over and :term:`publish`
      these files to their destinations.

   publish
      Publishing files does not mean that the files will be visible to the
      grand public. But rather it describes the process of putting (uploading,
      copying, ...) the files to a location defined as backup destination.

   module
      A general synonym for either :term:`generator_profile` or
      :term:`target_profile`

   profile
      A general synonym for either :term:`generator_profile` or
      :term:`target_profile`

.. _configuration:

Configuration
=============

The configuration file is a python file itself and can be placed wherever you
see fit.

This page explains the general configuration structure. Each :term:`module` may
provide additional configuration options.  They can be defined in each module's
``config`` dictionary. The details for each of these module-level configs can
be found in :ref:`available_plugins`.

Basic example
-------------

.. include:: config_examples/basic.rst

A configuration walkthrough
---------------------------

.. include:: config_examples/walkthrough.rst

Required values
---------------

The following values must be specified:

**CONFIG_VERSION**

   This is used by the core application to determine if it knows how to read
   the config file. If this value is incorrect, the core will issue
   errors/warnings.

   The value is a tuple representing a major and minor number.

   It follows the following rule:

      - If an application change *requires* a change in the config, the major
        number will increase.
      - If a change is made in the application which will still be able to
        function with an old config version, but may benefit from new fields,
        then the minor number will increase.

**STAGING_AREA**
   A *temporary* folder. All backup files will be created in that folder before
   pushed into the targets.

**GENERATORS**

   .. versionadded:: 1.1

   A list of generators. The generators will be processed in the same order as
   they appear in the config file. Each generator must have the following
   fields:

      ``name``
         The name of the generator. This is used to generate folder and
         filenames for the backup files.

      ``profile``
         The name of the :term:`module` used for this generator. See
         :ref:`available_plugins` for a list of available profiles.

      ``config``
         Config values for the generator profile. These fields depend on the
         underlying plugin. The values should be documented in
         :ref:`available_plugins`

**TARGETS**
   A list of backup targets. The targets will be processed in the same order as
   they appear in the config file. Each target must have the following fields:

      ``name``
         The name of the target (Mainly used to display it in the logs)

      ``profile``
         The name of the :term:`module` used for this target. See
         :ref:`available_plugins` for a list of available profiles.

      ``config``
         Config values for the target profile. These fields depend on the
         underlying plugin. The values should be documented in
         :ref:`available_plugins`

**SOURCES**

   .. deprecated:: 1.1

   Use ``GENERATORS`` instead

Advanced Example
----------------

.. include:: config_examples/advanced.rst

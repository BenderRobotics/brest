.. _api:

API
===

.. module:: brest

This part of the documentation covers all the interfaces of Brest.

Resource instantiation
----------------------

.. autoclass:: Resources
    :members:

.. autoclass:: ResourceProvider
    :members:

Config
------

.. autoclass:: Config
    :members:
    
Helper Methods
--------------

.. automethod:: helpers.overwrite_log_config
.. automethod:: helpers.prepare_tests

Devices
-------

Supplies
~~~~~~~~

.. currentmodule:: brest.supplies

Enumerations available for every supply:

.. autoclass:: brest.supplies::Supplies.Protection
    :members:

.. autoclass:: brest.supplies::Supplies.Kind
    :members:

Available supplies:

.. autoclass:: Tenma
    :members: enable, disable, voltage, current, enable_protection, disable_protection, get_info, connect, disconnect, check_connection, write, transceive
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

Communication
-------------

.. currentmodule:: brest.communication

.. autoclass:: SerialCommunicable
    :members: connect, disconnect, write_raw, read_raw, probe

.. autoclass:: SCPICommunicable 
    :members:

.. autoclass:: SCPICommand

    .. attribute:: cmd

        Plaintext command

.. autoclass:: SCPIValueCommand

    .. attribute:: cmd

        Plaintext command

    .. attribute:: value

        String representation of given value

Devices
-------

Supplies
~~~~~~~~

.. currentmodule:: brest.supplies

Supplies base class:

.. autoclass:: Supplies
    :members: Protection, Kind, Model, IDN, CHANNELS, MEMORIES, MAX_VOLTAGE, MAX_CURRENT, PROTECTION, KIND, _apply_model_specs

Available supplies:

.. autoclass:: Mansup
    :members:

.. autoclass:: Tenma
    :members: enable, disable, voltage, current, enable_protection, disable_protection, save_memory, recall_memory, get_info
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

    .. attribute:: channel

        Number of channel

.. autoclass:: SCPIQueryCommand

    .. attribute:: query_char

        Character that indicates query command. '?' is default

.. autoclass:: SCPIValueCommand

    .. attribute:: value

        Value that is converted to string and concatenated with delimiter

    .. attribute:: delimiter

        Character that is used to delimit value from the command

.. autoclass:: InterfaceCommunicable
    :members:

.. autoclass:: CLICommunicable
    :members:

.. autoclass:: NoneCommunicable

Messages
--------

.. autoclass:: Packable
    :members:

.. autoclass:: CommunicationStructure
    :members:

.. autoclass:: CommunicationFrame

Packable types
~~~~~~~~~~~~~~

.. currentmodule:: brest.communication.types

.. autoclass:: uint8_t
.. autoclass:: uint16_t
.. autoclass:: sint16_t
.. autoclass:: uint32_t
.. autoclass:: str_t
.. autoclass:: bool_t
.. autoclass:: bit_t
.. autoclass:: nlist_t
.. autoclass:: bit_nlist_t
.. autoclass:: checksum_t
.. autoclass:: pad_t

Devices
-------

Base class for all devices

.. currentmodule:: brest

.. autoclass:: Resource
    :members: name, disable_on_destruct

Supplies
~~~~~~~~

.. currentmodule:: brest.supplies

Supplies base class:

.. autoclass:: Supplies
    :members: Protection, Kind, Model, IDN, CHANNELS, MEMORIES, MAX_VOLTAGE, MAX_CURRENT, PROTECTION, KIND, _apply_model

Available supplies:

.. autoclass:: Mansup
    :members:

.. autoclass:: Tenma
    :members: enable, disable, voltage, current, enable_protection, disable_protection, save_memory, recall_memory, get_info

IO
~~

.. currentmodule:: brest.io

Input/Output base class:

.. autoclass:: IO
    :members: Model, IDN, CHANNELS, MAX_CURRENT, IS_LATCHING, __getitem__, __setitem__, get_states, aliases

Available devices:

.. autoclass:: USBRelay

Flashers
~~~~~~~~

.. currentmodule:: brest.flashers

Flashers base class:

.. autoclass:: Flashers
    :members: log, timeout, flash, write, mass_erase, erase_sector, read, read_to_file, soft_reset

Available flashers:

.. autoclass:: STLink

.. autoclass:: JLink

Cameras
~~~~~~~

.. currentmodule:: brest.cameras

Cameras base class:

.. autoclass:: Cameras
    :members: cam, resolution

Available cameras:

.. autoclass:: GenericCamera
    :members: acquire_image, acquire_images

.. autoclass:: Backfly
    :members: acquire_image, acquire_images, configure_trigger, reset_trigger, get_info

Loads
~~~~~

.. currentmodule:: brest.loads

Loads base class:

.. autoclass:: Loads
    :members: MAX_CURRENT

Available loads:

.. autoclass:: Pli
    :members: enable, disable, current, get_info, clear, reset, self_test, detect_model

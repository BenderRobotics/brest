.. _api:

API
===

This part of the documentation covers all the interfaces of Brest.

.. _brest-tools-methods:

Brest tools methods
-------------------

.. autofunction:: brest::find_available_resource

.. autofunction:: brest::print_available

.. autofunction:: brest::print_taken

.. autofunction:: brest::print_all

.. autofunction:: brest::generate_config

Resource instantiation
----------------------

.. currentmodule:: brest

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

.. autoclass:: HIDCommunicable
    :members: connect, disconnect, release, read_raw, write_raw

.. autoclass:: ClewareCommunicable
    :members: get_connections

.. autoclass:: CLICommunicable
    :members:

.. autoclass:: NoneCommunicable

.. _modbus_api:

MODBUS
~~~~~~

.. currentmodule:: brest.communication.modbus

.. autoclass:: ModbusFrame

    .. attribute:: mba

        Modbus address

    .. attribute:: pdu

        This attribute will contain message according to
        defined mappings, or :class:`~brest.communication.CommunicationStructure`
        if functioncode has no defined PDU.

    .. attribute:: error_check

        As default CRC function is used `crcmod.predefined.mkCrcFun`

.. autoclass:: ModbusInterface
    :members:

.. autoclass:: ModbusGenericPDU
    :members:

.. autoclass:: ModbusPDUMapping
    :members:

.. autoclass:: ModbusPDUMappings
    :members:

Messages
--------

.. currentmodule:: brest.communication

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
.. autoclass:: enum_t
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
    :members: Protection, Kind, Model, IDN, CHANNELS, MEMORIES, MAX_VOLTAGE, MAX_CURRENT, PROTECTION, KIND

Available supplies:

.. autoclass:: Mansup
    :members:

.. autoclass:: MP71
    :members: enable, disable, voltage, current, voltage_limit, current_limit, get_info, get_status, release

.. py:class:: Owon
   
   Alias for :class:`~brest.supplies.MP71`. Supported implicitly by the resource provider config.

.. autoclass:: Tenma
    :members: enable, disable, voltage, current, enable_protection, disable_protection, save_memory, recall_memory, get_status, get_info

.. py:class:: MP72
   
   Alias for :class:`~brest.supplies.Tenma`. Supported implicitly by the resource provider config.

.. class:: Supplies.StatusMessage

    .. attribute:: cv

        Indicates if supply output is in CV mode

    .. attribute:: cc

        Indicates if supply output is in CC mode

    .. attribute:: protection

        Indicates if both protection are enabled

    .. attribute:: enabled

        Indicates if output is enabled

.. class:: Tenma.StatusMessage

    Inherits :class:`~brest.supplies.Supplies.StatusMessage`

    Additional bits defined based on the model's internal structure.

    .. attribute:: cv

        Indicates if supply output is in CV mode

    .. attribute:: cc

        Indicates if supply output is in CC mode

    .. attribute:: protection

        Indicates if both protection are enabled

    .. attribute:: enabled

        Indicates if output is enabled

Multimeters
~~~~~~~~~~~

.. currentmodule:: brest.multimeters

Multimeters base class:

.. autoclass:: Multimeters
    :members: Kind, Model

Available multimeters:

.. autoclass:: Manmulti
    :members:
        set_mode_voltage_dc, set_mode_voltage_ac, set_mode_current_dc, set_mode_current_ac,
        set_mode_temperature, set_mode_resistance, set_mode_capacitance, set_mode_frequency,
        measure_temperature, measure_frequency, measure_capacitance, measure_resistance,
        measure_voltage, measure_voltage_dc, measure_voltage_ac,
        measure_current, measure_current_dc, measure_current_ac

.. autoclass:: Multicomp
    :members:
        Ranges, Units, Modes, TempSensors,
        get_mode, is_mode, detect_model,
        set_mode_voltage_dc, set_mode_voltage_ac,
        set_mode_current_dc, set_mode_current_ac,
        set_mode_temperature, set_mode_resistance, set_mode_capacitance, set_mode_frequency,
        measure_temperature, measure_frequency, measure_capacitance, measure_resistance,
        measure_voltage, measure_voltage_dc, measure_voltage_ac,
        measure_current, measure_current_dc, measure_current_ac

.. py:class:: MP73
   
   Alias for :class:`~brest.multimeters.Multicomp`. Supported implicitly by the resource provider config.

.. autoclass:: brest.multimeters.MP71
    :members:
        Ranges, Units, Modes,
        get_mode, is_mode, detect_model,
        set_mode_voltage_dc, set_mode_voltage_ac,
        set_mode_current_dc, set_mode_current_ac,
        set_mode_resistance, set_mode_capacitance,
        measure_capacitance, measure_resistance,
        measure_voltage, measure_voltage_dc, measure_voltage_ac,
        measure_current, measure_current_dc, measure_current_ac

IO
~~

.. currentmodule:: brest.io

Input/Output base class:

.. autoclass:: IO
    :members: Model, IDN, CHANNELS, MAX_CURRENT, IS_LATCHING, __getitem__, __setitem__, get_states, aliases

Available devices:

.. autoclass:: Manio

.. autoclass:: USBRelay

Interfaces
~~~~~~~~~~

.. currentmodule:: brest.interfaces

.. autoclass:: SerialInterface


Flashers
~~~~~~~~

.. currentmodule:: brest.flashers

Flashers base class:

.. autoclass:: Flashers
    :members: log, timeout, flash, write, mass_erase, erase_sector, read, read_to_file, soft_reset

Available flashers:

.. autoclass:: JLink

.. autoclass:: MCULink

.. autoclass:: STLink

Cameras
~~~~~~~

.. currentmodule:: brest.cameras

Cameras base class:

.. autoclass:: Cameras
    :members: cam, resolution, acquire_image, acquire_images, start_video_record, stop_video_record

Available cameras:

.. autoclass:: Basler
    :members: acquire_image, get_info, configure_trigger, reset_trigger

.. autoclass:: GenericCamera

.. autoclass:: PointGrey
    :members: acquire_image, get_info, configure_trigger, reset_trigger

.. autoclass:: DisplaySniffer
    :members: acquire_image, get_info

.. admonition:: Display Sniffer usage

    You might need to set up a few things for the Display Sniffer package,
    please follow the instructions here: https://gitlab.benderrobotics.com/br/tools/display-sniffer/-/tree/master/sw?ref_type=heads#-windows


Loads
~~~~~

.. currentmodule:: brest.loads

Loads base class:

.. autoclass:: Loads
   :members: KNOWN, Protection, Mode, Quantity, Units, Model, enable, disable, current, voltage, get_info, clear, reset, self_test, detect_model, required_voltage_range, required_current_range
   :undoc-members:

Available loads:

.. autoclass:: Pli
    :members: enable, disable, current, get_info, clear, reset, self_test, detect_model

.. autoclass:: Tenma
   :members: enable, disable, trigger, detect_model, is_enabled, current, voltage, power, resistance, measure, mode, configure_dynamic_mode, configure_ocp_mode, recall_ocp_mode
   :show-inheritance:

Telemetry & Configuration Classes:

.. autoclass:: brest.loads.tenma.TenmaTelemetry
   :members:
   :undoc-members:

.. autoclass:: brest.loads.configs.tenma.TenmaDynamicCVConfig
   :members:

.. autoclass:: brest.loads.configs.tenma.TenmaDynamicCCConfig
   :members:

.. autoclass:: brest.loads.configs.tenma.TenmaDynamicCRConfig
   :members:

.. autoclass:: brest.loads.configs.tenma.TenmaDynamicCWConfig
   :members:

.. autoclass:: brest.loads.configs.tenma.TenmaOCPConfig
   :members:

Switches
~~~~~~~~

.. currentmodule:: brest.switches

Switches base class:

.. autoclass:: Switches
    :members: CHANNELS, STATES

Available switches:

.. autoclass:: ClewareSwitch

.. autoclass:: Manswitch

.. autoclass:: YepkitSwitch

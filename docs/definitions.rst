.. _definitions:

Definitions
===========

.. _definitions.interfaces:

Interfaces
----------

All supported interfaces are listed here with all available parameters. You don't have to
specify every possible attribute. Every interface has a specific attribute or group of
attributes that need to be defined in order to successfully create interface. Also devices
already defined in Brest have implicit interface definitions. To find out what is already
defined on device please refer to :ref:`supported`.

Serial
~~~~~~

This interface represents `COM` serial communication.

================= ==== ==================
Attribute name    Type Description
================= ==== ==================
**type**          str  Must be ``serial``
**vid**           int  Vendor ID
**pid**           int  Product ID
**serial_number** str  Serial number
================= ==== ==================

All following attributes corresponds with class :class:`serial.Serial` so
for possible values please refer to the class's docs.

====================== ===== =======================================
Attribute name         Type  Description
====================== ===== =======================================
**port**               str   COM/tty or ``None``
**baudrate**           int   Baud rate such as 9600 or 115200 etc
**bytesize**           int   Number of data bits
**parity**             bool  Enable parity checking
**stopbits**           int   Number of stop bits
**timeout**            float Set a read timeout value
**xonxoff**            bool  Enable software flow control
**rtscts**             bool  Enable hardware (RTS/CTS) flow control
**dsrdtr**             bool  Enable hardware (DSR/DTR) flow control
**write_timeout**      float Set a write timeout value
**inter_byte_timeout** float Inter-character timeout, ``None`` to
                             disable (default)
**exclusive**          bool  Set exclusive access mode (POSIX only).
                             A port cannot be opened in exclusive
                             access mode if it is already open in
                             exclusive access mode
====================== ===== =======================================

Attribute or groups of attributes that need to be defined:

* **port** - Brest will try to open communication on that port
* **vid** + **pid** - Brest will try to look up ``port`` in connected devices matching ``vid`` and ``pid``
* **vid** + **pid** + **serial_number** - Look up can be refined with ``serial_number``
* **serial_number** - Brest will try to look up ``port`` in connected devices matching only ``serial_number``

Camera
~~~~~~

This interface represents camera index and its library.

================= ==== =======================================
Attribute name    Type Description
================= ==== =======================================
**type**          str  Must be ``camera``
**vid**           int  Vendor ID
**pid**           int  Product ID
**serial_number** str  Serial number
**index**         int  Camera's index int its library listing
**lib**           str  Library needed to operate with camera
================= ==== =======================================

Attribute or groups of attributes that need to be defined:

* **index** - Brest will try to open communication with ``index`` th camera.

.. admonition:: On camera lookup and index

    Unfortunate cameras can't be looked up properly in current version, so you have to
    define it's index. Also index is custom numbered for every library.

.. _definitions.configuration-file:

Configuration file
------------------

Standard location for your configuration file path is ``~/.brest/config.yaml``.
This path will be auto-expanded in the :attr:`~brest.Config.BREST_CONFIG` constant
after Brest import. If you want to have configuration file in another location,
methods which works with configuration file have ``config`` attribute where you can
pass your new `absolute` path to the config file.

The file itself is written in `YAML`_ and parsed by `PyYAML`_ so you can use some
python objects in the configuration.

.. _YAML:   https://yaml.org/
.. _PyYAML: https://pyyaml.org/

File structure
~~~~~~~~~~~~~~

The structure that Brest understands goes like::

    project_name:
        group_name:
            resource_alias:
                class_name: str
                [class_attribute:]*
                interface:
                    [interface_attribute]+

So the example containing a single resource would look like::

    # Name of a project
    myProj:
        # Group of resources
        Supplies:
            # Custom alias for a resource
            supply:
                # Resource definitions
                class_name: 'Tenma'
                voltage: 40 # Class's specific attribute
                current: 0.3
                interface:
                    port: 'COM6'

First of all, you can have multiple projects in same configuration file. Just
start again without indentation and follow the same structure. To make configuration
file more readable you can put empty lines between projects.

What needs to be defined
~~~~~~~~~~~~~~~~~~~~~~~~

Every resource must have defined ``class_name`` or ``interface`` or both. You can also
define values for class's existing attributes on the same level of indentation.

If you omit ``interface`` definition, Brest will use implicit interface definition.
WARNING! Implicit definition may not always contain specifying information. For example
the :class:`~brest.supplies.Tenma` class has ``vid`` and ``pid`` but not ``serial_number``.
So if happen to be more than one Tenma supply connected to the system, you have no
guarantee on what ``port`` is your class created. For list of available classes and groups,
please refer to the :ref:`supported`.

If you want to be more specific, or set project dependent values for interface attributes,
you can do it by defining the interface attribute. Every interface's attribute must have an
extra level of indentation and be under the `interface:`. Everything you define is merged
with implicit definition with configuration file definitions having higher priority.
For list of available Interfaces and its attributes, please refer to the
:ref:`definitions.interfaces`.

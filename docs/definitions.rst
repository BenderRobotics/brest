.. _definitions:

Definitions
===========

.. _definitions.configuration-file:

Configuration file
------------------

Standard location for your configuration file path is ``~/.brest/config.yaml``.
This path will be auto-expanded in the :attr:`~brest.Config.BREST_USER_CONFIG` constant
after Brest import. If you want to have configuration file in another location,
methods which works with configuration file have ``user_config`` and ``project_config``
attributes where you can pass your new `absolute` path to the user of project
configuration file.

The file itself is written in `YAML`_ and parsed by `PyYAML`_ so you can use base
python objects in the configuration.

.. _YAML:   https://yaml.org/
.. _PyYAML: https://pyyaml.org/

File structure
~~~~~~~~~~~~~~

The structure that Brest understands goes like::

    project_name:                  # Mandatory
        resource_alias:            # Mandatory
            class_name: str        # Mandatory
            [default:]
                [attributes]*
            [required:]
                [attributes]*
            [aliases:]
                - channel: int     # Mandatory if aliases is used
                  name: str        # Mandatory if aliases is used
                  [propagate: bool]
            [interface:]
                [attributes]*

    # Attributes encapsulated in square brackets are not mandatory
    # * indicates 0 to n occurrences

So the example containing a single resource would look like::

    my_proj:
        tenma:
            class_name: 'supplies.Tenma'
            default:
                voltage: 30
                current: 0.3
                protection: 'OCP'
            required:
                voltage_range: [0, 30]
            aliases:
                - channel: 1
                  name: 'main'
                  propagate: True
                - channel: 0
                  name: 'backup'
            interface:
                port: 'COM10'

What needs to be defined
~~~~~~~~~~~~~~~~~~~~~~~~

First of all, you can have multiple projects in same configuration file. Just
start again without indentation and follow the same structure. To make configuration
file more readable you can put empty lines between projects.

Every resource must have defined ``class_name`` the rest can be omitted. The value of
the parameter can be just group name or group name + class name connected using dot.
If only group name is defined, Brest will instantiate first class which satisfies
requirements defined in ``required:`` and can set defaults defined in ``default:``.

To find out what you can define in each category please refer to :ref:`supported` and
select a desired group of devices to get common attributes for the group. Each device
can have defined additional attributes so checkout also devices if you are aiming for
specific class.

If you omit ``interface:`` definition, Brest will use implicit interface definition.
WARNING! Implicit definition may not always contain specifying information. For example
the :class:`~brest.supplies.Tenma` class has ``vid`` and ``pid`` but not ``serial_number``.
So if happen to be more than one Tenma supply connected to the system, you have no
guarantee on what ``port`` is your class created. For list of available classes and groups,
please refer to the :ref:`supported`.
Otherwise if you specify ``interface:`` the configuration file definition will be merged with
implicit definition.

.. _definitions.resource_definitions:

Available definitions for each resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`~brest.cameras.Cameras`::

    default:
        video_filename: str             # supported exptensions are .mov, .avi, .mpg, .mpeg, .mp4, .mkv, .wmv
        video_format: str               # default 'mp4'
        video_fps: int                  # default 20
        video_width: int                # default is the camera resolution
        video_text_color: tuple or str  # (R, G, B), default '#ffffff'
        video_text: str                 # default None

:class:`~brest.cameras.PointGrey`::

    default:
        trigger: str ('line0', 'line1', 'line2', 'line3', 'software')
        exposure: float (milliseconds; 0 - continuous)
        gain: float
        gamma: float
        framerate: float
        white_auto_balance: str ('off', 'once', 'on')

:class:`~brest.flashers.Flashers`::

    default:
        log: str ("continuous", "after", "none")
        device: str
        flashloader: abs_path
        frequency: int
        file: abs_path
        address: str
        port: str ("JTAG", "SWD")
        timeout: float

:class:`~brest.flashers.STLink`::

    # All attributes from Flashers group can be used
    default:
        verbosity: int (1, 2, 3)
        mode: str ("under_reset", "hotplug", "normal")
        reset: str ("sw", "hw", "core")

:class:`~brest.flashers.JLink`::

    # All attributes from Flashers group can be used
    default:
        flashloader: abs_path  # has no effect, JLinkDevices.xml is prioritized

:class:`~brest.interfaces.Interfaces`:

Follow the :ref:`definitions.interfaces` section down below.

:class:`~brest.io.IO`::

    required:
        is_latching: bool
        channels: int
        current: float
    aliases:
        - channel: int
          name: str
          default_value: bool
          propagate: bool

:class:`~brest.io.Manio`::

    # All attributes from IO group can be used
    default:
        bypass_user: True  # if True user will not be prompted when setting channels

:class:`~brest.io.USBRelay`::

    # All attributes from IO group can be used

:class:`~brest.loads.Loads`::

    default:
        current: float

:class:`~brest.supplies.Supplies`::

    default:
        voltage: float
        current: float
        model: str
    required:
        voltage_range: [float, float]
        current_range: [float, float]
    aliases:
        - channel: int
          name: str
          propagate: bool
          default:
            voltage: float
            current: float

:class:`~brest.Switches`::

    required:
        channels: int
    aliases:
        - channel: int
          name: str
          states: [str, ...]
          default:
            state: int or str (from states)

:class:`~brest.switches.ClewareSwitch`::

    interface:
        sn_timeout: float

.. admonition:: Default values for multichannel supplies

    If you happen to have multichannel power supply, values under
    `default:` group will apply ONLY to FIRST channel. To se default values
    for other channels, use the same notation but in alias definition.

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

All following attributes correspond with class :class:`serial.Serial` so
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

HID
~~~

This interface represents a hid device.

================= ==== =======================================
Attribute name    Type Description
================= ==== =======================================
**type**          str  Must be ``hid``
**vid**           int  Vendor ID
**pid**           int  Product ID
**serial_number** str  Serial number
**path**          int  Path to the device in operating system
================= ==== =======================================

* **vid** + **pid** - Brest will try to look up in connected devices matching ``vid`` and ``pid``
* **vid** + **pid** + **serial_number** - Look up can be refined with ``serial_number``
* **serial_number** - Brest will try to look up in connected devices matching only ``serial_number``

Flashers
~~~~~~~~

This interface satisfy brest needs on comunicable and identifies flashers
on your system. Communication with flasher mediates specific external utility.

================= ==== =======================================
Attribute name    Type Description
================= ==== =======================================
**type**          str  Must be ``flashers``
**utility**       str  An absolute path to cmd utility that
                       operates the flasher
**serial_number** str  Serial number
================= ==== =======================================

Camera
~~~~~~

This interface represents camera index and its library.

================= ==== =======================================
Attribute name    Type Description
================= ==== =======================================
**type**          str  Must be ``camera``
**index**         int  Camera's index int its library listing
**service**       str  Service name for camera on windows
                       machine. This field is implicitly
                       filled with a value.
**serial_number** str  Serial number
================= ==== =======================================

Attribute or groups of attributes that need to be defined:

* **index** + **service** - Brest will try to open communication with ``index`` th camera.

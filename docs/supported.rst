.. _supported:

Supported devices
=================

Here is a list of currently supported devices.

The first level indention indicates groups of resources. These names can be used
in ``group=`` keyword argument. These classes are not meant to be instantiated.

The second level of indention represent available resources.

* :class:`~brest.cameras.Cameras`

    * :class:`~brest.cameras.GenericCamera`
    * :class:`~brest.cameras.PointGrey`
    * :class:`~brest.cameras.Basler`

* :class:`~brest.flashers.Flashers`

    * :class:`~brest.flashers.JLink`
    * :class:`~brest.flashers.MCULink`
    * :class:`~brest.flashers.STLink`

* :class:`~brest.interfaces.Interfaces`

    * :class:`~brest.interfaces.SerialInterface`

* :class:`~brest.io.IO`

    * :class:`~brest.io.Manio`
    * :class:`~brest.io.USBRelay`

* :class:`~brest.loads.Loads`

    * :class:`~brest.loads.Pli`

* :class:`~brest.supplies.Supplies`

    * :class:`~brest.supplies.Mansup`
    * :class:`~brest.supplies.Tenma`

* :class:`~brest.multimeters.Multimeters`

    * :class:`~brest.multimeters.Multicomp`

* :class:`~brest.switches.Switches`

    * :class:`~brest.switches.Manswitch`
    * :class:`~brest.switches.ClewareSwitch`
    * :class:`~brest.switches.YepkitSwitch`

.. _developer:

Developer
=======================

Welcome to the internal developer documentation. This guide explains the application's specific implementation details, and provides instructions for contributions.

Resource Aliases
----------------

During initialization, the :class:`~brest.resource_provider.ResourceProvider` iterates through subclasses of :class:`~brest.resource.Resource`. For each discovered class, it checks for an ``ALIAS`` class attribute. If present, the resource is mapped in the internal class registry under both its original class name (e.g. ``multimeters.Multicomp``) and its alias (e.g. ``multimeters.MP73``).

**How to define and use them:**
You can define an alias by adding the ``ALIAS`` class attribute to your resource subclass. Brest supports both a single string or a list of strings:

.. code-block:: python

    class Multicomp(Multimeters):
        ALIAS = 'MP73'

    # Or using multiple aliases: 
    class Multicomp(Multimeters):
        ALIAS = ['MP73', 'MP730889']


Serial Communication Pool
-------------------------

Brest utilizes a global connection pool for serial communications, implemented in the :class:`~brest.communication.serial_communicable.SerialCommunicable` class. This mechanism allows multiple distinct logical resource instances to share a single physical serial port connection safely and efficiently.

**How it works:**
Whenever a new ``SerialCommunicable`` (or ``SCPICommunicable``) instance is initialized, the framework inspects the physical ``port`` (e.g. ``COM3`` or ``/dev/ttyUSB0``).
If the port is already registered in the global pool (``__POOL``), brest securely reuses the existing ``serial.Serial`` instance and increments an internal reference counter (``refs``). 
If not, a new physical connection is opened, bound to an access lock (``threading.RLock``), and registered in the pool.

When instances are destroyed or explicitly released via the ``.release()`` method, the reference counter decrements. Note that the physical port is only closed globally once the last reference referencing that port has been safely released.

**Concurrency and Thread Safety:**
Each pooled connection holds its individual reentrant lock (``access_lock``). All raw serial read/write transactions are safely wrapped within this lock. This strictly prevents concurrent resource collisions and race conditions where multiple hardware devices (like distinct SCPI channels on the same chassis) send queries simultaneously over the very same physical line. Additionally, the ``transceive`` method implemented in the :class:`~brest.communication.scpi_communicable.SCPICommunicable` class is thread-safe.

**How to add a new device using the pool:**
1. Your device driver should inherit from either :class:`~brest.communication.serial_communicable.SerialCommunicable` or, more commonly, :class:`~brest.communication.scpi_communicable.SCPICommunicable`.
2. It's completely transparent: just pass the target interface (containing the ``port``) into your parent class constructor (e.g., ``SCPICommunicable.__init__(self, params['interface'])``).
3. The framework handles pooling, locking, and reusing automatically under the hood.
4. You can leverage pooled metadata using ``self._set_metadata(key, value)`` and ``self._get_metadata(key)``. Metadata is bound to the connection port, allowing multiple logical devices using the same port to securely share states (like a dynamic ``message_suffix``).

Note that when fetching the ``message_suffix`` from pooled metadata, the mechanism defaults to ``self.SUFFIXES[0]`` if the suffix hasn't been definitively probed yet.

**Known limitations**

**Sequential Locking Bottleneck:** Because pooled transmission locks the port, communication across multiple logically pooled devices occurs completely sequentially. Firing concurrent high-frequency I/O requests to multiple devices on the same shared port could become a performance bottleneck due to IO wait times.

**Static Interface Settings:** You cannot initialize two devices with differing serial configurations (like ``baudrate`` or ``parity``) onto the same pooled port dynamically without breaking connection synchrony. Ensure that devices mapped to identical physical hardware ports declare the exact same serial baud rates and data formats.

**Strict Lifecycles:** Failing to invoke ``.release()`` causes lingering zombie references in the background pool. Your connection will never cleanly disconnect, which might crash subsequent probing algorithms unless Python garbage cleans the dangling references.

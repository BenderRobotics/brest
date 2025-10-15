.. _installation:

Installation
============

.. _installation.download-and-install-latest-release:

Download and install latest release
------------------------------------

.. code-block:: sh

    $ pip install brest

Brest should be installed now. You can now head to the :ref:`usage` or install Optional dependencies.

.. _installation.python-version:

Python version
--------------

Brest supports Python versions 3.x >= 3.5 on Windows and Linux.

.. warning::

    Usage on Python >= 3.8 may be possible, but is not fully verified yet.

.. note::

    * Main supported Python versions:
        * 3.7 - tested by time (end-of-life in June 2023)
        * 3.10 - current aim (should be stable enough and last long enough)

    .. image:: images/python_schedule_20240130.png
      :alt: Python version schedule
      :align: center
      :target: https://devguide.python.org/versions/

    * *(updated in January 2024)*

.. admonition:: pip on Linux

    In some distributions ``pip`` is not installed by default. Make sure you have it installed before
    installing Brest.

.. _installation.python-dependencies:

Python dependencies
-------------------

Core
~~~~

* These dependencies will be installed automatically when installing Brest:
    * `colorama`_ (==0.4.6) - Colored terminal output
    * `pyserial`_ (==3.5) - Serial communication
    * `PyYAML`_ (==6.0.1) - YAML files parsing
    * `Cython`_ (==0.29.36) - C extensions in Python
    * `hidapi`_ (==0.14.0) - Cython hidapi interface
    * `crcmod`_ (==1.7) - CRC generator

.. _colorama: https://pypi.org/project/colorama/
.. _pyserial: https://pypi.org/project/pyserial/
.. _PyYAML: https://pypi.org/project/PyYAML/
.. _Cython: https://pypi.org/project/Cython/
.. _hidapi: https://pypi.org/project/hidapi/
.. _crcmod: https://pypi.org/project/crcmod/

.. _installation.python-resource-specific:

Resource specific
~~~~~~~~~~~~~~~~~

These dependencies will not be installed automatically. Brest will detect and
use them if you install them using following command:

.. code-block:: sh

    $ pip install brest[optional_dependency_name]

* :code:`cameras_win`
    * Run on Windows machine.
    * Installs libraries for Brest to be able to list and use `OpenCV`_ operable cameras.
* :code:`cameras_unix`
    * Run on Unix machine.
    * Installs libraries for Brest to be able to use `OpenCV`_ operable cameras.
    * .. note:: Brest cannot **list** cameras on Unix machines.
* :code:`docs`
    * Enables user to build Brest documentation using `Sphinx`_.
* :code:`jlink_win`
    * Enables Brest to discover JLink devices.

.. _OpenCV: https://pypi.org/project/opencv-python/
.. _Sphinx: http://www.sphinx-doc.org/en/master/

.. note:: This method will only work if you already have Brest installed.

.. _installation.external-dependencies:

External dependencies
---------------------

Resource specific
~~~~~~~~~~~~~~~~~

These dependencies will not be installed automatically. Brest will try to detect them and
use them if you install them.

* `JLink`_
    * Install this program so Brest will be able to list and use J-Link programmers.
    * It is recommended to install the program in the path used by :class:`~brest.flashers.JLink`.
    * .. note:: Make sure to have the required resource specific Python dependencies installed (see :ref:`above<installation.python-resource-specific>`).
* `MCUXpressoIDE`_
    * Install this program so Brest will be able to list and use the NXP MCU-Link programmers.
    * It is recommended to install the program in a path similar to the path used by :class:`~brest.flashers.MCULink`.
    * .. note:: The path is specific for each release of the IDE, hence the specific path mentioned might not be the correct one.
* `STM32_Programmer_CLI`_
    * Install this program so Brest will be able to list and use ST-Link programmers
    * It is recommended to install the program in the path used by :class:`~brest.flashers.STLink`

.. _JLink: https://www.segger.com/downloads/jlink/
.. _MCUXpressoIDE: https://www.nxp.com/design/software/development-software/mcuxpresso-software-and-tools-/mcuxpresso-integrated-development-environment-ide:MCUXpresso-IDE
.. _STM32_Programmer_CLI: https://www.st.com/en/development-tools/stm32cubeprog.html

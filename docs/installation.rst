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

Brest supports Python 3.5 and above on Windows and Linux.

.. admonition:: pip on Linux

    In some distributions ``pip`` is not installed by default. Make sure you have it installed before
    installing Brest.

.. _installation.python-dependencies:

Python dependencies
-------------------

Core
~~~~

These dependencies will be installed automatically when installing Brest:

* `colorama`_ (>=0.4.1) - Colored terminal output
* `pyserial`_ (>=3.4) - Serial communication
* `PyYAML`_ (>=5.1.2) - YAML files parsing

.. _colorama: https://pypi.org/project/colorama/
.. _pyserial: https://pypi.org/project/pyserial/
.. _PyYAML:   https://pypi.org/project/PyYAML/

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
    * **NOTE:** Brest cannot list cameras on Unix machines.
* :code:`docs`
    * Enables user to build Brest documentation using `Sphinx`_.

.. _OpenCV: https://pypi.org/project/opencv-python/
.. _Sphinx: http://www.sphinx-doc.org/en/master/

.. warning:: This method will only work if you already have Brest installed.

.. _installation.external-dependencies:

External dependencies
---------------------

Resource specific
~~~~~~~~~~~~~~~~~

These dependencies will not be installed automatically. Brest will try to detect them and
use them if you install them.

* `STM32_Programmer_CLI`_
    * Install this program so Brest will be able to list and use ST-Link programmers
    * It is recommended to install program in path used by :class:`~brest.flashers.STLink`
* `JLink`_
    * Install this program so Brest will be able to list and use J-Link programmers
    * It is recommended to install program in path used by :class:`~brest.flashers.JLink`

.. _STM32_Programmer_CLI: https://www.st.com/en/development-tools/stm32cubeprog.html
.. _JLink: https://www.segger.com/downloads/jlink/

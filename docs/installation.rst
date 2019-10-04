.. _installation:

Installation
============

Download and install latest release
------------------------------------

Pro tip: You can't

After you have downloaded the file, navigate to its directory and execute the following command to install Brest:

.. code-block:: sh

    $ pip install brest-0.0.1--py3-none-any.whl

Brest should be installed now. You can now head to the :ref:`usage` or install Optional dependencies.

Python version
--------------

Brest supports Python 3.5 and above on Windows and Linux

.. admonition:: pip on Linux

    In some distributions ``pip`` is not installed by default. Make sure you have it installed before
    installing Brest.

Dependencies
------------

These dependencies will be installed automatically when installing Brest

* `colorama`_ (>=0.4.1) - Colored terminal output
* `pyserial`_ (>=3.4) - Serial communication
* `PyYAML`_ (>=5.1.2) - YAML files parsing

.. _colorama: https://pypi.org/project/colorama/
.. _pyserial: https://pypi.org/project/pyserial/
.. _PyYAML:   https://pypi.org/project/PyYAML/

Optional dependencies
---------------------
These dependencies will not be installed automatically. Brest will detect and
use them if you install them using following command:

.. code-block:: sh

    $ pip install brest[optional_dependency_name]

This method will only work if you already have Brest installed.

* cameras_win - Install this on Windows machine so Brest will be able to list and use `OpenCV`_ operable cameras
* cameras_unix - Install this on Unix machine so Brest will be only able to use `OpenCV`_ operable cameras, but won\'t list then
* docs - You will be able to build Brest documentation using `Sphinx`_

.. _OpenCV: https://pypi.org/project/opencv-python/
.. _Sphinx: http://www.sphinx-doc.org/en/master/

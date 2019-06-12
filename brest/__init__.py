##
# @file   Supplies/__init__.py
# @brief  Supplies init file - sets up the log subsystem
#
# @copyright copyright 2019, Bender Robotics, All rights reserved
#
# @addtogroup Supplies
# @{

import os
import sys

BREST_CONFIG_PATH = os.path.expanduser('~/brest')
BREST_CONFIG_NAME = 'brest.yaml'
BREST_CONFIG      = '{0}/{1}'.format(BREST_CONFIG_PATH, BREST_CONFIG_NAME)

# This explicitly sets our path so that we can use all modules in root folder.
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

# Add config default position to path
path = os.path.abspath(BREST_CONFIG_PATH)
if not (os.path.exists(path)):
    os.mkdir(path)
if not path in sys.path:
    sys.path.insert(1, path)
del path

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Resources():

    class Generic():

        @classmethod
        def available(cls):
            raise NotImplementedError('Listing of available resources is not supported for {0} class.'.format(cls.__name__))

        @classmethod
        def probe(cls, resource):
            raise NotImplementedError('{0} class does not support probing for specific devices.'.format(cls.__name__))

        @classmethod
        def get(cls, **kwargs):
            raise NotImplementedError('{} instances do not support filtered factory instantiation.'.format(cls.__name__))


from brest.supplies.tenma import Tenma
from brest.supplies.virsup import Virsup


# @}
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

# This explicitly sets our path so that we can use all modules in root folder.
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

# TO-DO: make automatic
from supplies.tenma import Tenma
from supplies.virsup import Virsup

# @}
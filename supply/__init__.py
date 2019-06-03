##
# @file   supply/__init__.py
# @brief  Supply init file - sets up the log subsystem
#
# @copyright copyright 2019, Bender Robotics, All rights reserved
#
# @addtogroup supply
# @{

import os
import sys

# this explicitely sets our path so that we can use the pycm modules
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

# @}
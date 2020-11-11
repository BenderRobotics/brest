#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.switches.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~

    This file signifies that 'switches' is a module.

    :copyright: 2020 Bender Robotics
"""

from .switches import Switches
from .cleware_switch import ClewareSwitch
from .manswitch import Manswitch

__all__ = ['Switches', 'ClewareSwitch', 'Manswitch']

__version__ = '0.0.9'

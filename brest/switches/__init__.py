#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.switches.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~

    This file signifies that 'switches' is a module.

    :copyright: 2022 Bender Robotics
"""

from .switches import Switches
from .cleware_switch import ClewareSwitch
from .manswitch import Manswitch
from .yepkit import YepkitSwitch

__all__ = [
    'Switches',
    'ClewareSwitch',
    'Manswitch',
    'YepkitSwitch',
]

__version__ = '0.0.13'

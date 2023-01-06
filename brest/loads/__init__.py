#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.loads.__init__
    ~~~~~~~~~~~~~~~~~~~~

    This file signifies that 'loads' is a module.

    :copyright: 2023 Bender Robotics
"""

from .loads import Loads
from .pli import Pli

__all__ = ['Loads', "Pli"]

__version__ = '0.0.10'

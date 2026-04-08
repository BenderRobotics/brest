#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.supplies.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~

    This file signifies that 'supplies' is a module.

    :copyright: 2024 Bender Robotics
"""

from .supplies import Supplies
from .mansup import Mansup
from .tenma import Tenma
from .mp71 import MP71

__all__ = ['Supplies', 'Mansup', 'Tenma', 'MP71']

__version__ = '1.0.0'

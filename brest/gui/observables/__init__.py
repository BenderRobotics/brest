#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.gui.observables.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file signifies that 'observables' is a module.

    :copyright: 2024 Bender Robotics
"""

from .observable import Observable
from .observable_dict import ObservableDict

__all__ = [
    'Observable',
    'ObservableDict',
]

__version__ = '0.0.14'

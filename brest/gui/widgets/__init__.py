#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.gui.widgets.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file signifies that 'widgets' is a module.

    :copyright: 2023 Bender Robotics
"""

from .frame_switcher import FrameSwitcher
from .editor import Editor
from .scrollable_frame import ScrollableFrame

__all__ = [
    'FrameSwitcher',
    'Editor',
    'ScrollableFrame',
]

__version__ = '0.0.14'

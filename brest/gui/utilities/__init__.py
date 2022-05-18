#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.gui.utilities.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file signifies that 'utilities' is a module.

    :copyright: 2022 Bender Robotics
"""

from .text_syntax_highliting import TextSyntaxHighlight
from .treeview_methods import dict_to_treeview

__all__ = [
    'TextSyntaxHighlight',
    'dict_to_treeview',
]

__version__ = '0.0.14'

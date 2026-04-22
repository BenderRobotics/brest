#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.gui.views.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This file signifies that 'views' is a module.

    :copyright: 2024 Bender Robotics
"""

from .resource_view import ResourceView
from .config_view import ConfigView
from .project_view import ProjectView
from .project_resource_view import ProjectResourceView

__all__ = [
    'ResourceView',
    'ConfigView',
    'ProjectView',
    'ProjectResourceView',
]

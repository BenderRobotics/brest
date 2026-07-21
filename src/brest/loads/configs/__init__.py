#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.loads.configs.__init__
    ~~~~~~~~~~~~~~~~~~~

    This file signifies that 'configs' is a module.

    :copyright: 2026 Bender Robotics
"""

from .tenma import TenmaDynamicCVConfig, TenmaDynamicCCConfig, TenmaDynamicCRConfig, TenmaDynamicCWConfig, TenmaOCPConfig

__all__ = [
    'TenmaDynamicCCConfig',
    'TenmaDynamicCRConfig',
    'TenmaDynamicCVConfig',
    'TenmaDynamicCWConfig',
    'TenmaOCPConfig',
]

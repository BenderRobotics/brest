#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.interfaces.interfaces
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements base abstract class for interface.

    :copyright: 2022 Bender Robotics
"""

from brest import Resource

class Interfaces(Resource):
    """
    Base class for representing communication interface.

    :param params: Construction parameters
    :type  params: dict
    """

    KNOWN = {}

    def __init__(self, params = None):
        Resource.__init__(self, params)

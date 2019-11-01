# -*- coding: utf-8 -*-
"""
    brest.loads.loads
    ~~~~~~~~~~~~~~~~~

    This module implements base abstract class for loads.

    :copyright: 2019 Bender Robotics
"""

from brest import Resource

class Loads(Resource):
    """
    Base class for representing a electrical load
    """

    KNOWN = {}

    def __init__(self, params = None):
        Resource.__init__(self, params)

        #: Maximum possible current
        self.MAX_CURRENT = None

    def enable(self):
        """
        Enables load.
        """

        raise NotImplementedError('This load cannot be enabled.')

    def disable(self):
        """
        Disable loads.
        """

        raise NotImplementedError('This load cannot be disabled.')

    @property
    def current(self):
        """
        Gets and sets desired amount of current.
        """

        raise NotImplementedError('This load is unable to measure output current.')

    @current.setter
    def current(self):
        raise NotImplementedError('This load does not support different current limits.')

    def get_info(self):
        """
        Return info string.
        """

        raise NotImplementedError('This load has no means of status detection.')

    def clear(self):
        """
        Clears load's registers.
        """

        raise NotImplementedError('This load does not support registers clear.')

    def reset(self):
        """
        Resets load to default values.
        """

        raise NotImplementedError('This load does not support reset to default values.')

    def self_test(self):
        """
        Self test.
        """

        raise NotImplementedError('This load does not support self testing.')

    def detect_model(self, apply = True):
        """
        Implicitly tries to apply model's electrical limits.
        """

        raise NotImplementedError('This load does not support specific model detection.')

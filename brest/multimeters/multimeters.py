#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.multimeters.multimeters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements base abstract for multimeters.

    :copyright: 2024 Bender Robotics
"""

from brest import Resource
from enum import Enum


class Multimeters(Resource):
    """
    Base class for representing a multimeter.
    """
    KNOWN = {}

    class Kind(Enum):
        """
        Enumeration supported kinds of multimeters, based on the output type.
        """

        #: Manual multimeter
        MANUAL = 1

        #: Programmable multimeter
        PROGRAMMABLE = 2

    class Model():
        """
        Model info.

        :param idn: Identification string
        :type  idn: str
        :param max_sample_freq: maximum sample rate (samples per second)
        :type  max_sample_freq: int
        :param ac_bandwidth_min: AC True RMS measurement bandwidth minimum [Hz]
        :type  ac_bandwidth_min: int
        :param ac_bandwidth_min: AC True RMS measurement bandwidth maximum [Hz]
        :type  ac_bandwidth_min: int
        :param internal_memory: Can save measured data and display it in a table
        :type  internal_memory: Bool
        :param kind: Kind of multimeter
        :type  kind: list of :class:`~brest.multimeters.Multimeters.Kind`
        """

        def __init__(self, idn, max_sample_freq, ac_bandwidth_min, ac_bandwidth_max, internal_memory, kind):
            self.idn = idn
            self.max_sample_freq = max_sample_freq
            self.ac_bandwidth_min = ac_bandwidth_min
            self.ac_bandwidth_max = ac_bandwidth_max
            self.internal_memory = internal_memory
            self.kind = kind

        def __str__(self):
            s = ''
            s += '{}: {}\n'.format('idn', self.idn)
            s += '{}: {}\n'.format('max_sample_freq', self.max_sample_freq)
            s += '{}: {}\n'.format('ac_bandwidth', self.ac_bandwidth)
            s += '{}: {}\n'.format('internal_memory', self.internal_memory)
            s += '{}: {}\n'.format('kind', self.kind.name)
            return s

    def __init__(self, params=None):
        Resource.__init__(self, params)
        #: Model number
        self.IDN = None
        #: Maximum sample frequency
        self.MAX_SAMPLE_FREQ = 0
        #: AC measurement bandwidth minimum
        self.AC_BANDWIDTH_MIN = 0
        #: AC measurement bandwidth maximum
        self.AC_BANDWIDTH_MAX = 0
        #: has internal memory
        self.INTERNAL_MEMORY = False
        #: Kind of a multimeter
        self.KIND = None

        self._aliases = {}
        self._propagate = []
        self._channels = []

    def _apply_model(self, model):
        """
        Applies model info to the class.

        :param model: Model's specification you want to apply
        :type  model: :class:`~brest.multimeters.Multimeters.Model`
        """

        self.IDN = model.idn
        self.MAX_SAMPLE_FREQ = model.max_sample_freq
        self.AC_BANDWIDTH_MIN = model.ac_bandwidth_min
        self.AC_BANDWIDTH_MAX = model.ac_bandwidth_max
        self.INTERNAL_MEMORY = model.internal_memory
        self.KIND = model.kind

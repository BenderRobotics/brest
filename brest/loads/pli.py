# -*- coding: utf-8 -*-
"""
    brest.loads.loads
    ~~~~~~~~~~~~~~~~~

    This module implements base abstract class for loads.

    :copyright: 2019 Bender Robotics
"""

from brest.loads import Loads
from brest.communication import SCPICommunicable, SCPICommand, SCPIQueryCommand, SCPIValueCommand, CommunicableError

class Pli(Loads, SCPICommunicable):
    """
    Pli programmable electric supply.

    Derived from: :class:`~brest.loads.Loads`, :class:`~brest.communication.SCPICommunicable`

    Implicit interface::

        interface:
            type: 'serial'
            timeout: 0.1
            baudrate: 115200

    Because Pli electric load is connected using an converter, you
    have to alway specify vid, pid or serial_number.
    """

    Loads.KNOWN['Pli'] = {
        'type': 'serial',
        'timeout': 0.1,
        'baudrate': 115200,
        'vid': 0x0000,
        'pid': 0x0000,
    }

    class Commands():
        GET_INFO    = SCPIQueryCommand("*IDN")
        CLEAR       = SCPICommand("*CLS")
        RESET       = SCPICommand("*RST")
        SELF_TEST   = SCPIQueryCommand("*TST")
        SET_CURR    = SCPIValueCommand("CURR")
        GET_CURR    = SCPIQueryCommand("CURR")
        EN_INPUT    = SCPICommand("INP ON")
        DIS_INPUT   = SCPICommand("INP OFF")
        GET_INPUT   = SCPIQueryCommand("INP")

    def __init__(self, params):
        Loads.__init__(self)
        SCPICommunicable.__init__(self, params['interface'])
        self.message_suffix = '\n'

        self.determine_suffix(self.Commands.GET_INFO)

    def __del__(self):
        self.unmark_taken(self)

    def enable(self):
        self.transceive(Pli.Commands.EN_INPUT)

    def disable(self):
        self.transceive(Pli.Commands.DIS_INPUT)

    @property
    def current(self):
        return float(self.transceive(Pli.Commands.GET_CURR))

    @current.setter
    def current(self, value):
        Pli.Commands.SET_CURR.value = value
        self.transceive(Pli.Commands.SET_CURR)

    def get_info(self):
        return self.transceive(Pli.Commands.GET_INFO)

    def clear(self):
        return self.transceive(Pli.Commands.CLEAR)

    def reset(self):
        return self.transceive(Pli.Commands.RESET)

    def self_test(self):
        return int(self.transceive(Pli.Commands.SELF_TEST))

    def default_current(self, value):
        self.current = value
        return True

    def detect_model(self):
        pass

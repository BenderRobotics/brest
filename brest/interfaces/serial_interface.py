# -*- coding: utf-8 -*-
"""
    brest.communication.serial_communicable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements represeting com port as a resource.

    :copyright: 2019 Bender Robotics
"""

from .interfaces import Interfaces

from brest.communication import SerialCommunicable

class SerialInterface(Interfaces, SerialCommunicable):
    """
    Class for represeting com port as a resource. Underlying
    object for serial communication is accessible using
    ``com`` attribute. Port needs to be opened first.

    Derived from :class:`~brest.interfaces.Interfaces`,
    :class:`~brest.communication.SerialCommunicable`

    :param params: Construction params
    :type  params: dict
    """

    Interfaces.KNOWN['SerialInterface'] = {
        'type': 'serial',
        'vid': 0x0000,
        'pid': 0x0000,
        }

    def __init__(self, params):
        Interfaces.__init__(self, params)
        SerialCommunicable.__init__(self, params['interface'])
        self.disconnect()

    def detect_model(self):
        pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.modbus.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file signifies that 'modbus' is a module.

    :copyright: 2020 Bender Robotics
"""

from .modbus_interface import ModbusInterface
from .definitions import ModbusFrame, ModbusPDUMapping, ModbusGenericPDU, ModbusPDUMappings

__all__ = [
    'ModbusFrame',
    'ModbusInterface',
    'ModbusPDUMapping',
    'ModbusGenericPDU',
    'ModbusPDUMappings',
    ]

__version__ = '0.0.9'

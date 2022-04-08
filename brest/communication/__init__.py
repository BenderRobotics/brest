#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file signifies that 'communication' is a module.

    :copyright: 2021 Bender Robotics
"""

from .communicable import Communicable, CommunicableError
from .serial_communicable import SerialCommunicable
from .communicable_structures import Endianness, Packable, CommunicationStructure, CommunicationFrame
from .scpi_communicable import SCPICommunicable, SCPICommand, SCPIQueryCommand, SCPIValueCommand
from .camera_communicable import CameraCommunicable
from .none_communicable import NoneCommunicable
from .frame_communication_interface import FrameCommunicationInterface
from .interface_communicable import InterfaceCommunicable
from .flasher_communicable import FlasherCommunicable
from .hid_communicable import HIDCommunicable
from .cli_communicable import CLICommunicable
from .cleware_communicable import ClewareCommunicable

import types

__all__ = [
    'Communicable',
    'CommunicableError',
    'Endianness',
    'Packable',
    'CommunicationStructure',
    'CommunicationFrame',
    'PackableTypes',
    'SerialCommunicable',
    'SCPICommunicable',
    'SCPICommand',
    'SCPIQueryCommand',
    'SCPIValueCommand',
    'CameraCommunicable',
    'NoneCommunicable',
    'FrameCommunicationInterface',
    'InterfaceCommunicable',
    'FlasherCommunicable',
    'HIDCommunicable',
    'CLICommunicable',
    'ClewareCommunicable',
    'types',
    ]

__version__ = '0.0.14'

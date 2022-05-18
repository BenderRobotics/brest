#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.none_communicable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements a class for devices with no communication
    to fit Brest.

    :copyright: 2022 Bender Robotics
"""

from brest.communication import Communicable

class NoneCommunicable(Communicable):
    """
    Class for devices with no communication

    Use this class for devices which operates only as a
    software and has no physical connections.
    """

    TYPE = 'none'
    TAKEN = []
    SETTINGS = []

    def __init__(self, params):
        Communicable.__init__(self)

    def get_connections(self):
        return []

    def probe(self, interface, connections = None):
        return interface

    def mark_taken(self, interface):
        pass

    def is_taken(self, interface):
        return False

    def get_available(self, class_name, interface, connections):
        return [
            {'class_name': class_name, 'interface': {'type': 'none'}},
        ]

    def format_interface(self, interface):
        attrs = []
        # Called on constructed object
        if isinstance(interface, NoneCommunicable):
            attrs.append(('type', interface.TYPE))
        # Called on interface dict
        elif isinstance(interface, dict):
            for name, value in interface.items():
                attrs.append((name, value))
        return attrs

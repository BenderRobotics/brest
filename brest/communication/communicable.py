#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.communicable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements base abstract for communication.

    :copyright: 2024 Bender Robotics
"""


class CommunicableError(Exception):
    """
    Exception representing an error during communication.
    """

    pass


class Communicable():
    """
    Base class for communication interfaces.
    """

    def connect(self):
        """
        Tries to connect to the interface.
        """

        raise NotImplementedError('This interface doesn\'t implement connection')

    def disconnect(self):
        """
        Tries to disconnect from the interface.
        """

        raise NotImplementedError('This interface doesn\'t implement disconnection')

    def release(self):
        """
        Releases bound connections to the system.
        """

        raise NotImplementedError('This interface doesn\'t implement physical binding releasing')

    def check_connection(self):
        """
        Checks if connection is able to send a receive messages.
        """

        raise NotImplementedError('This interface doesn\'t implement connection check')

    def write_raw(self, data):
        """
        Writes bytes like object directly into the connection.
        """

        raise NotImplementedError('This interface doesn\'t implement raw data writing')

    def read_raw(self, expected='', size=None):
        """
        Reads directly from the connection and returs bytes like object.
        """

        raise NotImplementedError('This interface doesn\'t implement raw data reading')

    def write(self, message):
        """
        Accepts CommunicalbeStructure as a message.
        Sends message in a blocking mode.
        Should use write_raw to send the message.
        """

        raise NotImplementedError('This interface doesn\'t implement message write')

    def transceive(self, message):
        """
        Accepts CommunicalbeStructure as a message. Sends and receives message in a blocking mode.
        Should use write_raw, read_raw to send and receive the message.
        """

        raise NotImplementedError('This interface doesn\'t implement transceive communication')

    def write_async(self, message):
        """
        Accepts CommunicalbeStructure as a message.
        Sends message in a non-blocking mode.
        Should use write_raw to send the message.
        """

        raise NotImplementedError('This interface doesn\'t implement message write')

    def transceive_async(self, message):
        """
        Accepts CommunicalbeStructure as a message.
        Sends and receives message in a non-blocking mode.
        Should use write_raw, read_raw to send and receive the message.
        """

        raise NotImplementedError('This interface doesn\'t implement transceive communication')

    def get_connections(self):
        """
        Returns physical connection into the machine.
        """

        raise NotImplementedError('This interface doesn\'t implement getting physical connections')

    def probe(self, interface, connections=None):
        """
        Returns connection(s) matching given interface.
        """

        raise NotImplementedError('This interface doesn\'t implement connections probing')

    def extra_probe(self, interface, device):
        """
        If device needs extra steps to determine certain properties, use this method. Is called before
        any property checks during probing.
        """

        pass

    def mark_taken(self, interface):
        """
        Marks given interface as taken. Such interface won't be listed or used again.
        """

        raise NotImplementedError('This interface doesn\'t implement taken interface marking')

    def is_taken(self, interface):
        """
        Returs if given interface is taken or not.
        """

        raise NotImplementedError('This interface doesn\'t implement taken checking')

    def get_available(self, class_name, interface, connected):
        """
        Returns list of parameter for resources, that can be constructed.
        """

        raise NotImplementedError('This interface doesn\'t implement listing available resources')

    def format_interface(self, interface):
        """
        Formats interface to human readable format.
        """

        raise NotImplementedError('This interface doesn\'t implement interface printing in human readable format')

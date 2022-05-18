#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.interface_communicable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements communication using serial line and
    described frames.

    :copyright: 2022 Bender Robotics
"""

import logging
import threading
import struct

from brest.communication import SerialCommunicable

# --------- future implementation ------------
#import queue

class InterfaceCommunicable(SerialCommunicable):
    """
    Class that provides unified interface for frame communication

    Derived from :class:`~brest.communication.SerialCommunicable`

    Method :meth:`~brest.communication.InterfaceCommunicable._read_raw_frame`
    must be implemented in order to use this interface.
    """

    def __init__(self, params):
        SerialCommunicable.__init__(self, params)

        self.port_lock = threading.Lock()

        # --------- future implementation ------------
        #self.write_thread = threading.Thread(target=self.write_loop)
        #self.read_thread  = threading.Thread(target=self.read_loop)
        #self.transceive_event = threading.Event()
        #self.write_queue  = queue.SimpleQueue()
        #self.frame_queue  = queue.SimpleQueue()
        #self.WRITE_TIMEOUT = 0.025

    def write(self, frame):
        frame.pack()
        self.port_lock.acquire()
        self.write_raw(frame.raw_data)
        self.port_lock.release()

    def transceive(self, frame, resp_type):
        frame.pack()

        self.port_lock.acquire()
        self.write_raw(frame.raw_data)
        rec_frame = self._read_raw_frame()
        self.port_lock.release()

        if not rec_frame.is_frame_valid(rec_frame, frame):
            return None

        rec_frame.change_data_type(resp_type)
        try:
            rec_frame.unpack()
        except struct.error as ex:
            self.logger.error('Error during frame unpacking: {}'.format(str(ex)), extra=self.log_args)
            return None

        return rec_frame.get_data()

    def _read_raw_frame(self, frame):
        """
        Method which muset be implemented. Should read correct number of bytes into frame.raw_data.
        """

        raise NotImplementedError('{} must implement _read_raw_frame(self, frame) method'.format(self.__class__.__name__))

    def get_frame(self, *args, **kwargs):
        """
        Method which must be implemented. Shoud return new or deep copy of a frame used in the communication.
        """

        raise NotImplementedError('{} must implement get_frame(self, frame) method'.format(self.__class__.__name__))

    # --------- future implementation ------------

    def write_async(self, frame):
        """
        Adds frame into outgoing messages pool. Don\'t except an answer.
        """

        raise NotImplementedError

    def transceive_async(self, frame, resp_type):
        """
        Adds frame into outgoing messages pool. Except answer and call an appropriate callback.
        """

        raise NotImplementedError

    def write_loop():
        """
        Will be executed in tread responsible for message sending.
        """

        raise NotImplementedError

    def read_loop():
        """
        Will be executed in tread responsible for message receiving.
        """

        raise NotImplementedError

    def subscribe():
        """
        Bonds callback method to a signal.
        """

        raise NotImplementedError

    def unsubscribe():
        """
        Unbonds callback method from a signal.
        """

        raise NotImplementedError

# -*- coding: utf-8 -*-
"""
    brest.communication.frame_communication_interface
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module defines general communication which uses frames.

    :copyright: 2020 Bender Robotics
"""

import logging
import threading
import struct

from .communicable import Communicable

# --------- future implementation ------------
#import queue

class FrameCommunicationInterface():
    """
    Class that provides unified interface for frame communication


    Method :meth:`~brest.communication.CommunicationInterface._read_raw_frame`
    must be implemented in order to use this interface.
    """

    def __init__(self, params):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        self.port_lock = threading.Lock()

        # --------- future implementation ------------
        #self.write_thread = threading.Thread(target=self.write_loop)
        #self.read_thread  = threading.Thread(target=self.read_loop)
        #self.transceive_event = threading.Event()
        #self.write_queue  = queue.SimpleQueue()
        #self.frame_queue  = queue.SimpleQueue()
        #self.WRITE_TIMEOUT = 0.025

    def transceive(self, frame, resp_type):
        """
        Method which muset be implemented.
        """

        raise NotImplementedError('{} must implement transceive(self, frame, resp_type) method'.format(self.__class__.__name__))

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

    def read_async(self, frame):
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

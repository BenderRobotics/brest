#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @name:
#   virsup.py
#
#  @brief:
#   Virtual power supply class for demonstration purposes.
#
#  Copyright 2019 Bender Robotics

import logging
from supply.supply import Supply

class Virsup(Supply.Generic):

    '''
    '''
    def __init__(self, port=None):
        #super().__init__()

        logging.get_logger(__name__)
        self.port = port
        self.com = None

        if (None == self.port):
            self.port = self.probe()
        if (None != self.port):
            self.connect()
            self.detect()

    '''
    '''
    def connect(self, port=None, baud=PORT_BAUD):
        logging.info('Connected to virtual supply.')

    '''
    '''
    def disconnect(self):
        logging.info('Disconnected from virtual supply.')

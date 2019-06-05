#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @name:
#   virsup.py
#
#  @brief:
#   Virtual power Supplies class for demonstration purposes.
#
#  Copyright 2019 Bender Robotics

import logging
from supplies.supplies import Supplies

class Virsup(Supplies.Generic):
    '''
    '''

    def __init__(self, port=None):
        '''

        '''

        #logging.get_logger(__name__)
        self.port = port
        self.com = None

        if (None == self.port):
            self.port = self.probe()
        if (None != self.port):
            self.connect()
            self.detect()

    def connect(self, port=None, baud=None):
        '''

        '''

        #logging.info('Connected to virtual supply.')
        print ('Connected to virtual supply.')

    def disconnect(self):
        '''

        '''

        #logging.info('Disconnected from virtual supply.')
        print ('Disconnected from virtual supply.')

    def detect(self):
        '''

        '''

        #logging.info('Detected generic virtual supply.')
        print ('Detected generic virtual supply.')
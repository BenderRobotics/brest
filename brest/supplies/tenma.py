#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @name:
#   tenma.py
#
#  @brief:
#   Tenma power supply fake class for demonstration purposes.
#
#  Copyright 2019 Bender Robotics

from brest.supplies import Supplies
from brest.communication import SerialCommunicable

class Tenma(Supplies, SerialCommunicable):

    PORT_TIMEOUT  = 0.050

    class Commands():
        GET_ID      = '*IDN?'
        GET_STATUS  = 'STATUS?'
        SET_VOLTAGE = 'VSET1?'
        GET_VOLTAGE = 'VOUT1?'
        SET_CURRENT = 'ISET1?'
        GET_CURRENT = 'IOUT1?'
        EN_OUTPUT   = 'OUT1'
        DIS_OUTPUT  = 'OUT0'
        EN_OVP      = 'OVP1'
        DIS_OVP     = 'OVP0'
        EN_OCP      = 'OCP1'
        DIS_OCP     = 'OCP0'
        RECALL      = 'RCL1'
        SAVE        = 'SAV1'


    Models = [
        Supplies.Model('TENMA 72-2535', 1, 30.0, 3.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-2540', 1, 30.0, 5.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-2545', 1, 60.0, 2.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
        Supplies.Model('TENMA 72-2550', 1, 60.0, 3.0, [Supplies.Protection.OCP, Supplies.Protection.OVP], Supplies.Kind.PROGRAMMABLE),
    ]

    def __init__(self, kwargs):
        Supplies.__init__(self)
        SerialCommunicable.__init__(self, kwargs)
        
        self.parse_args(kwargs)

        self.connect()
        self.detect()

    def connect(self):
        '''

        '''

        if self.com and not self.com.isOpen():
            try:
                self.com.open()
            except:
                pass #TO-DO

    def disconnect(self):
        '''

        '''

        if self.com and self.com.isOpen():
            try:
                self.com.close()
            except:
                pass #TO-DO

    def apply_model_specs(self, model):
        self.model_name = model.psu_idn
        self.CHANNELS = model.channels
        self.MAX_VOLTAGE = model.max_voltage
        self.MAX_CURRENT = model.max_current
        self.protection = model.protection
        self.kind = model.kind

    def detect(self):
        '''
        Method which tries to determine specific electrical limits of the supply based on IDN retrieval.
        '''

        psu_idn = self.trancieve(Tenma.Commands.GET_ID)

        for model in self.Models:
            if (model.idn in psu_idn):
                self.apply_model_specs(model)
        if (None == self.model_name):
            print ('Unable to detect type of the PSU.')    

    def trancieve(self, command, modifier = None):
        '''

        '''

        try:
            # Assemble message
            if (modifier == None):
                # If no modifier is sent, send whole command
                msg = command
            else:
                if (command[-1:] == '?'):
                    # Some messages require different format
                    msg = command[:-1] + ':' + modifier
                else:
                    msg = command + modifier
            # Send message to serial port
            self.com.write(msg.encode('utf-8'))
            # Get response
            recv = ''
            while(True):
                char = str(self.com.read(1), 'utf-8')
                if ('' == char):
                    break
                recv += char
            return recv
        except Exception as e:
            print(e)
            pass

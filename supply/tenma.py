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

import serial
import serial.tools.list_ports

from supply.supply import Supply

class Tenma(Supply.Generic):

    '''
    '''
    PORT_BAUD     = 9600
    PORT_TIMEOUT  = 0.050

    '''

    '''
    TENMA_VID = 0x416   # Winbond Electronics Corporation
    TENMA_PID = 0x5011  # Virtual Com Port

    '''
    '''
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

    '''
    '''
    class Model():

        def __init__(self, idn, channels, voltage, current, protection):
            self.idn = idn
            self.channels = channels
            self.voltage = voltage
            self.current = current
            self.protection = protection

    Models = [
        Model('TENMA 72-2535', 1, 30.0, 3.0, [Supply.Protection.OCP, Supply.Protection.OVP]),
        Model('TENMA 72-2540', 1, 30.0, 5.0, [Supply.Protection.OCP, Supply.Protection.OVP]),
        Model('TENMA 72-2545', 1, 60.0, 2.0, [Supply.Protection.OCP, Supply.Protection.OVP]),
        Model('TENMA 72-2550', 1, 60.0, 3.0, [Supply.Protection.OCP, Supply.Protection.OVP]),
    ]

    '''
    '''
    def __init__(self, port=None):
        #super().__init__()

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
        if (None == self.com):
            try:
                if (None != port):
                    self.port = port
                self.com = serial.Serial(
                    self.port,
                    baud,
                    timeout=Tenma.PORT_TIMEOUT,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                )
            except:
                raise
        else:
            try:
                self.com.open()
            except:
                raise

    '''
    '''
    def disconnect(self):
        try:
            self.com.close()
        except:
            pass #TO-DO

    '''
    '''
    #def probe(self):
    #    # List all available comports currently present in the system
    #    coms = serial.tools.list_ports.comports()

    #    for com in coms:
    #        if Tenma.TENMA_VID == com.vid and Tenma.TENMA_PID == com.pid:
    #            # TO-DO: Handle case of more than one port available
    #            print('Detected Tenma type PSU @{0}'.format(com.device))
    #            return com.device
    '''
    Method which tries to determine specific electrical limits of the supply based on IDN retrieval.
    '''
    def detect(self):
        psu_idn = self._send_command(Tenma.Commands.GET_ID)

        for model in self.Models:
            if (model.idn in psu_idn):
                self.name = psu_idn
                print ('Detected {0} PSU'.format(self.name))
        if (None == self.name):
            print ('Unable to detect type of the PSU.')

    # Internal methods

    '''
    '''
    def _send_command(self, command, modifier = None):
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

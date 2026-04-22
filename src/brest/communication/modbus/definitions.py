#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.modbus.definitions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements unified interface for MODBUS communication.

    :copyright: 2024 Bender Robotics
"""

from enum import Enum
from brest.communication import Endianness
from brest.communication import CommunicationStructure, CommunicationFrame
from brest.communication.types import uint8_t, uint16_t, uint32_t, vlist_t, checksum_t

from crcmod.predefined import mkCrcFun


class ModbusFrame(CommunicationFrame):
    """
    Represents generic modbus frame. Allows to set PDU/data, computes error check.
    """

    def __init__(self, pdu_mapping=None):
        CommunicationFrame.__init__(self)

        self.add('mba', uint8_t())
        self.add('pdu', CommunicationStructure())
        self.add('error_check', checksum_t(uint16_t, self.compute_error_check), byteorder=Endianness.LITTLE)

        self.pdu_mapping = pdu_mapping
        self.valid = False
        self.direct_response = False
        self.exception = False
        self.len = None
        self.modbus_crc_func = mkCrcFun('modbus')

    def compute_error_check(self, data):
        """
        Default methor for crc calculation (Modbus CRC16). Override to compute non-standard error_check.
        """

        return self.modbus_crc_func(bytes(data))

    def set_data(self, mba=None, pdu=None):
        """
        Method for filling the frame.
        """

        if mba is not None and pdu is not None:
            self.mba = mba
            self.change('pdu', pdu)
        elif pdu is not None:
            self.change('pdu', pdu)
        else:
            raise ValueError

    def change_data_type(self, msg_type):
        """
        Changes the data type class to another to be able to unpacked successfully.
        """

        self.change('pdu', msg_type)

    def change_pdu_type(self, msg_type):
        """
        Changes the pdu type class to another to be able to unpacked successfully.
        """

        self.change('pdu', msg_type)

    def get_data(self):
        """
        Returns the PDU part of the frame.
        """

        # pylint: disable=no-member
        return self.pdu
        # pylint: enable=no-member

    def is_frame_valid(self, rec_frame, sent_frame):
        """
        Checks function_code.
        """

        # Response with the same code
        if sent_frame.pdu.function_code == rec_frame.pdu.function_code:
            # self.logger.debug('Frame valid - regular response', extra=self.log_args)
            return True
        if ((sent_frame.pdu.function_code | 0x80) == rec_frame.pdu.function_code):
            # self.logger.debug('Frame valid - exception response', extra=self.log_args)
            return True
        else:
            self.logger.warning(
                msg=(
                    'Frame invalid - sent: {}, rec: {}'
                    ''.format(sent_frame.pdu.function_code, rec_frame.pdu.function_code)
                ),
                extra=self.log_args
            )
            return False


class ModbusGenericPDU(CommunicationStructure):
    """
    Represents generic Modbus PDU
    """

    def __init__(self):
        CommunicationStructure.__init__(self, byteorder=Endianness.BIG)


class ModbusPDUMapping():
    """
    Holds one Modbus PDU mapping

    Mapping:
        - Function code
        - Request PDU
        - Response PDU
    """

    def __init__(self, functioncode, request, response):
        self.function_code = functioncode
        self.request = request
        self.response = response


class ModbusPDUMappings():
    """
    Represents list of Modbus PDU mappings.
    """

    def __init__(self, mappings):
        self.mappings = mappings

    def get_dict(self):
        """
        Returns all available mappings as dictionary.
        """

        return self.mappings

    def get_mapping(self, functioncode=None, name=None):
        """
        Returns mapping based on functioncode or name.
        """

        ret_mapping = None

        if functioncode is not None:
            for name, mapping in self.mappings.items():
                if functioncode == mapping['function_code']:
                    ret_mapping = mapping
        elif name is not None:
            ret_mapping = self.mappings[name]
        return ret_mapping

    def list_mappings(self):
        """
        Lists all available mappings.
        """

        for name, mapping in self.mappings.items():
            print("\nCommand:", name)

            for item in mapping:
                print(item + ':', mapping[item])


class ModbusFunctionCodes:
    """
    List of public Modbus Function Codes
    """

    READ_COILS = 0x01
    READ_DISCRETE_INPUTS = 0x02
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04
    WRITE_SINGLE_COIL = 0x05
    WRITE_SINGLE_REGISTER = 0x06
    READ_EXCEPTION_STATUS = 0x07
    DIAGNOSTICS = 0x08
    GET_COM_EVENT_COUNTER = 0x0B
    GET_COM_EVENT_LOG = 0x0C
    WRITE_MULTIPLE_COILS = 0x0F
    WRITE_MULTIPLE_REGISTERS =  0x10
    REPORT_SERVER_ID = 0x11
    READ_FILE_RECORD = 0x14
    WRITE_FILE_RECORD = 0x15
    MASK_WRITE_REGISTER = 0x16
    READ_WRITE_MULTIPLE_REGISTERS = 0x17
    READ_FIFO_QUEUE = 0x18
    READ_DEVICE_IDENTIFICATION = 0x43


class ModbusExceptionCodes(Enum):
    """
    List of Modbus Exceptions
    """

    ILLEGAL_FUNCTION = 0x01
    ILLEGAL_DATA_ADDRESS = 0x02
    ILLEGAL_DATA_VALUE = 0x03
    SLAVE_DEVICE_FAILURE = 0x04
    ACKNOWLEDGE = 0x05
    SLAVE_DEVICE_BUSY = 0x06
    NEGATIVE_ACKNOWLEDGE = 0x07
    MEMORY_PARITY_ERROR = 0x08
    GATEWAY_PATH_UNAVAILABLE = 0x0A
    GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND = 0x0B

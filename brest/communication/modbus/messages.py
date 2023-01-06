#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.modbus.messages
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements unified interface for MODBUS communication.

    :copyright: 2023 Bender Robotics
"""

from brest.communication.types import uint8_t, uint16_t, uint32_t, vlist_t, checksum_t
from .definitions import ModbusGenericPDU, ModbusPDUMapping, ModbusFunctionCodes

# ----------------------------------------------------------------------

class ReadCoilsRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('start_address', uint16_t())
        self.add('quantity', uint16_t())

class ReadCoilsResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('byte_count', uint8_t())
        self.add('coil_status', vlist_t(None, uint8_t), len_attr='byte_count')

# ----------------------------------------------------------------------

class ReadDiscreteInputsRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('start_address', uint16_t())
        self.add('quantity', uint16_t())

class ReadDiscreteInputsResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('byte_count', uint8_t())
        self.add('input_status', vlist_t(None, uint8_t), len_attr='byte_count')

# ----------------------------------------------------------------------

class ReadHoldingRegistersRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('start_address', uint16_t())
        self.add('quantity', uint16_t())

class ReadHoldingRegistersResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('byte_count', uint8_t())
        self.add('data_value', vlist_t(None, uint16_t), len_attr='byte_count')

# ----------------------------------------------------------------------

class ReadInputRegistersRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('start_addr', uint16_t())
        self.add('quantity', uint16_t())

class ReadInputRegistersResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('byte_count', uint8_t())
        self.add('data_value', vlist_t(None, uint16_t), len_attr='byte_count')

# ----------------------------------------------------------------------

class WriteSingleCoilRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('output_address', uint16_t())
        self.add('output_value', uint16_t())

class WriteSingleCoilResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('output_address', uint16_t())
        self.add('output_value', uint16_t())

# ----------------------------------------------------------------------

class WriteSingleRegisterRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('register_address', uint16_t())
        self.add('register_value', uint16_t())

class WriteSingleRegisterResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('register_address', uint16_t())
        self.add('register_value', uint16_t())

# ----------------------------------------------------------------------

class ReadExceptionStatusRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())

class ReadExceptionStatusResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('output_data', uint8_t())

# ----------------------------------------------------------------------

class DiagnosticsRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('sub_function', uint16_t())
        self.add('data', vlist_t(None, uint16_t))

class DiagnosticsResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('sub_function', uint16_t())
        self.add('data', vlist_t(None, uint16_t))

# ----------------------------------------------------------------------

class GetComEventCounterRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())

class GetComEventCounterResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('status', uint16_t())
        self.add('event_count', uint16_t())

# ----------------------------------------------------------------------

class GetComEventLogRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())

class GetComEventLogResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('byte_count', uint8_t())
        self.add('status', uint16_t())
        self.add('event_count', uint16_t())
        self.add('message_count', uint16_t())
        self.add('events', vlist_t(None, uint8_t))

# ----------------------------------------------------------------------

class WriteMultipleCoilsRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('start_address', uint16_t())
        self.add('quantity', uint16_t())
        self.add('byte_count', uint8_t())
        self.add('outputs_value', vlist_t(None, uint8_t), len_attr='byte_count')

class WriteMultipleCoilsResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('start_address', uint16_t())
        self.add('quantity', uint16_t())
# ----------------------------------------------------------------------

class WriteMultipleRegistersRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('start_address', uint16_t())
        self.add('quantity', uint16_t())
        self.add('byte_count', uint8_t())
        self.add('register_value', vlist_t(None, uint16_t), len_attr='byte_count')

class WriteMultipleRegistersResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('start_address', uint16_t())
        self.add('quantity', uint16_t())

# ----------------------------------------------------------------------

class ReportServerIDRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())

class ReportServerIDResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('byte_count', uint8_t())
        self.add('server_id', vlist_t(None, uint8_t))
        self.add('run_indicator_status', uint8_t())
        self.add('additional_data', vlist_t(None, uint8_t))

# ----------------------------------------------------------------------

class ReadFileRecordRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('byte_count', uint8_t())
        self.add('sub_requests', ModbusGenericPDU())

class ReadFileRecordResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('response_data_length', uint8_t())
        self.add('sub_requests', ModbusGenericPDU())

# ----------------------------------------------------------------------

class WriteFileRecordRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('request_data_length', uint8_t())
        self.add('sub_requests', ModbusGenericPDU())

class WriteFileRecordResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('response_data_length', uint8_t())
        self.add('sub_requests', ModbusGenericPDU())

# ----------------------------------------------------------------------

class MaskWriteRegisterRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('reference_address', uint16_t())
        self.add('and_mask', uint16_t())
        self.add('or_mask', uint16_t())

class MaskWriteRegisterResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('reference_address', uint16_t())
        self.add('and_mask', uint16_t())
        self.add('or_mask', uint16_t())

# ----------------------------------------------------------------------

class ReadWriteMultipleRegistersRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('read_start_address', uint16_t())
        self.add('read_quantity', uint16_t())
        self.add('write_start_address', uint16_t())
        self.add('read_quantity', uint16_t())
        self.add('write_byte_count', uint8_t())
        self.add('write_registers_value', vlist_t(None, uint16_t), len_attr='write_byte_count')

class ReadWriteMultipleRegistersResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('byte_count', uint8_t())
        self.add('reference_address', uint16_t())
        self.add('read_registers_value', vlist_t(None, uint16_t), len_attr='byte_count')

# ----------------------------------------------------------------------

class ReadFIFOQueueRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('fifo_pointer_address', uint16_t())

class ReadFIFOQueueResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('byte_count', uint16_t())
        self.add('fifo_count', uint16_t())
        self.add('fifo_register_value', vlist_t(None, uint16_t), len_attr='fifo_count')

# ----------------------------------------------------------------------

class ReadDeviceIdentificationRequest(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('mei_type', uint8_t())
        self.add('mei_data', ModbusGenericPDU())

class ReadDeviceIdentificationResponse(ModbusGenericPDU):

    def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('mei_type', uint8_t())
        self.add('mei_data', ModbusGenericPDU())

# ----------------------------------------------------------------------

class ExceptionResponse(ModbusGenericPDU):

   def __init__(self):
        ModbusGenericPDU.__init__(self)
        self.add('function_code', uint8_t())
        self.add('exception_code', uint8_t())

# ----------------------------------------------------------------------

MODBUS_MAPPINGS = {
    'ReadCoils': ModbusPDUMapping(ModbusFunctionCodes.READ_COILS,
                                  ReadCoilsRequest,
                                  ReadCoilsResponse
                                 ).__dict__,

    'ReadDiscreteInputs': ModbusPDUMapping(ModbusFunctionCodes.READ_DISCRETE_INPUTS,
                                           ReadDiscreteInputsRequest,
                                           ReadDiscreteInputsResponse
                                          ).__dict__,

    'ReadHoldingRegisters': ModbusPDUMapping(ModbusFunctionCodes.READ_HOLDING_REGISTERS,
                                             ReadHoldingRegistersRequest,
                                             ReadHoldingRegistersResponse
                                            ).__dict__,

    'ReadInputRegisters': ModbusPDUMapping(ModbusFunctionCodes.READ_INPUT_REGISTERS,
                                           ReadInputRegistersRequest,
                                           ReadInputRegistersResponse
                                          ).__dict__,

    'WriteSingleCoil': ModbusPDUMapping(ModbusFunctionCodes.WRITE_SINGLE_COIL,
                                        WriteSingleCoilRequest,
                                        WriteSingleCoilResponse
                                       ).__dict__,

    'WriteSingleRegister': ModbusPDUMapping(ModbusFunctionCodes.WRITE_SINGLE_REGISTER,
                                            WriteSingleRegisterRequest,
                                            WriteSingleRegisterResponse
                                           ).__dict__,

    'ReadExceptionStatus': ModbusPDUMapping(ModbusFunctionCodes.READ_EXCEPTION_STATUS,
                                            ReadExceptionStatusRequest,
                                            ReadExceptionStatusResponse
                                           ).__dict__,

    'Diagnostics': ModbusPDUMapping(ModbusFunctionCodes.DIAGNOSTICS,
                                    DiagnosticsRequest,
                                    DiagnosticsResponse
                                   ).__dict__,

    'GetComEventCounter': ModbusPDUMapping(ModbusFunctionCodes.GET_COM_EVENT_COUNTER,
                                           GetComEventCounterRequest,
                                           GetComEventCounterResponse
                                          ).__dict__,

    'GetComEventLog': ModbusPDUMapping(ModbusFunctionCodes.GET_COM_EVENT_LOG,
                                       GetComEventLogRequest,
                                       GetComEventLogResponse
                                      ).__dict__,

    'WriteMultipleCoils': ModbusPDUMapping(ModbusFunctionCodes.WRITE_MULTIPLE_COILS,
                                           WriteMultipleCoilsRequest,
                                           WriteMultipleCoilsResponse
                                          ).__dict__,

    'WriteMultipleRegisters': ModbusPDUMapping(ModbusFunctionCodes.WRITE_MULTIPLE_REGISTERS,
                                               WriteMultipleRegistersRequest,
                                               WriteMultipleRegistersResponse
                                              ).__dict__,

    'ReportServerID': ModbusPDUMapping(ModbusFunctionCodes.REPORT_SERVER_ID,
                                       ReportServerIDRequest,
                                       ReportServerIDResponse
                                      ).__dict__,

    'ReadFileRecord': ModbusPDUMapping(ModbusFunctionCodes.READ_FILE_RECORD,
                                       ReadFileRecordRequest,
                                       ReadFileRecordResponse
                                       ).__dict__,

    'WriteFileRecord': ModbusPDUMapping(ModbusFunctionCodes.WRITE_FILE_RECORD,
                                        WriteFileRecordRequest,
                                        WriteFileRecordResponse
                                       ).__dict__,

    'MaskWriteRegister': ModbusPDUMapping(ModbusFunctionCodes.MASK_WRITE_REGISTER,
                                          MaskWriteRegisterRequest,
                                          MaskWriteRegisterResponse
                                         ).__dict__,

    'ReadWriteMultipleRegisters': ModbusPDUMapping(ModbusFunctionCodes.READ_WRITE_MULTIPLE_REGISTERS,
                                                   ReadWriteMultipleRegistersRequest,
                                                   ReadWriteMultipleRegistersResponse
                                                  ).__dict__,

    'ReadFIFOQueue': ModbusPDUMapping(ModbusFunctionCodes.READ_FIFO_QUEUE,
                                      ReadFIFOQueueRequest,
                                      ReadFIFOQueueResponse
                                      ).__dict__,

    'ReadDeviceIdentification': ModbusPDUMapping(ModbusFunctionCodes.READ_DEVICE_IDENTIFICATION,
                                                 ReadDeviceIdentificationRequest,
                                                 ReadDeviceIdentificationResponse
                                                 ).__dict__
}

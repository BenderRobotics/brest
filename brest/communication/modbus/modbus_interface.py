#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.modbus.modbus_interface
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements unified interface for MODBUS communication.

    :copyright: 2022 Bender Robotics
"""

import threading
import queue
import time

from brest.communication import FrameCommunicationInterface
from brest.communication.types import uint8_t, uint16_t, checksum_t
from .definitions import ModbusFrame, ModbusPDUMappings
from .messages import MODBUS_MAPPINGS, ExceptionResponse

class ModbusInterface(FrameCommunicationInterface):
    """
    Class that provides unified interface for modbus communication

    Derived from :class:`~brest.communication.FrameCommunicationInterface`

    Method :meth:`~brest.communication.CommunicationInterface._read_raw_frame`
    must be implemented in order to use this interface.
    """

    def __init__(self, params):
        FrameCommunicationInterface.__init__(self, params)
        self.run_thread = True
        self.comm_thread = threading.Thread(target=self._comm_loop)
        self.comm_thread.daemon = True

        self.transceive_event = threading.Event()
        self.write_queue = queue.SimpleQueue()
        self.read_queue = queue.SimpleQueue()
        self.WRITE_TIMEOUT = 0.025
        self.TRANSACTION_TIMEOUT = 0.5
        self.COMM_LOOP_DELAY = 0.01
        self.WRITE_READ_DELAY = 0.01
        self.INTERMESSAGE_DELAY = 0.01
        self.default_pdu_mappings = ModbusPDUMappings(MODBUS_MAPPINGS)
        self.custom_pdu_mappings = None
        self.use_default_mappings = True

        self.comm_thread.start()

    def write(self, frame):
        """
        Writes data from frame using write_raw method.
        """

        self.port_lock.acquire()
        self.com.reset_input_buffer()
        self.write_raw(frame.raw_data)
        self.port_lock.release()


    def _read_raw_frame(self, frame):
        """
        Method which muset be implemented. Should read correct number of bytes into frame.raw_data.

        Frame parameter is optional, new frame generation can be handled inside the function.
        """

        raise NotImplementedError('{} must implement _read_raw_frame(self, frame) method'.format(self.__class__.__name__))

    def set_custom_pdu_mappings(self, mappings):
        """
        Method for storing project specific mappings for general use.
        """
        self.custom_pdu_mappings = mappings

    def get_mapping_from_fc(self, functioncode):
        """
        Returns mapping from available mappings based on function code.

        First checks custom mappings, then checks default mappings if no match is found.
        """

        if self.custom_pdu_mappings is not None:
            if self.custom_pdu_mappings.get_mapping(functioncode) is not None:
                return self.custom_pdu_mappings.get_mapping(functioncode)

        if (self.default_pdu_mappings.get_mapping(functioncode) is not None
            and self.use_default_mappings):

            return self.default_pdu_mappings.get_mapping(functioncode)
        return None

    def get_frame(self, mba=None, functioncode=None, data=None, pdu_mapping=None):
        """
        Method for getting new frame.
        Use 1: No parameters are specified, returns empty ModbusFrame.
        Use 2: mba, functioncode and data are specified, returns ModbusFrame request filled according to available mappings.
        Use 3: mba, pdu_mapping and data are specified, returns ModbusFrame request filled according to provided mapping.
        Use 4: Only functioncode is specified, returns ModbusFrame response according to available mappings.
        Use 3: pdu_mapping is specified, returns ModbusFrame response according to provided mapping.
        """

        frame = ModbusFrame()

        # Empty frame
        if mba is None and functioncode is None and data is None and pdu_mapping is None:
            return frame

        if mba is None:
            raise ValueError('No Target Address.')

        pdu = None
        mapping = None

        # Use mapping from input
        if pdu_mapping is not None:
            mapping = pdu_mapping
            pdu = mapping['request']()
            pdu.function_code = mapping['function_code']

        # Use custom or default mappings based on functioncode
        elif functioncode is not None:
            mapping = self.get_mapping_from_fc(functioncode)
            if mapping is not None:
                pdu = mapping['request']()
                pdu.function_code = mapping['function_code']
            else:
                self.logger.warning('Functioncode does not have mapping. fc:{}'.format(functioncode),
                                  extra=self.log_args)

        # Try to recover functioncode from data
        if mapping is None and data is not None:
            fc = data[0]
            mapping = self.get_mapping_from_fc(fc)
            if mapping is not None:
                pdu = mapping['request']()
                pdu.function_code = fc
            else:
                self.logger.warning('Functioncode from data does not have mapping. fc:{}'.format(functioncode),
                                  extra=self.log_args)

        if mapping is None:
            raise ValueError('Could not determine frame format. No mapping matches inputs.')

        # Fill data
        if data is not None:
            try:
                pdu.unpack(data)
            except:
                self.logger.error('Data insert failed. (Used pdu.unpack)', extra=self.log_args)

        # Fill frame
        frame.pdu_mapping = mapping
        frame.set_data(mba, pdu)
        return frame

    def transceive(self, frame):
        """
        Method for one communication transaction.
        Sends frame, blocks until read timeout and returns frame if available.
        """
        response = None

        self._print_request_info(frame)
        self.write_async(frame)

        response = self.read()
        if response is not None:
            if response.valid:
                self._print_response_info(response)
            else:
                self._print_raw_response(response)
        return response

    def read(self):
        """
        Method for reading frame in blocking mode.
        Blocks until read timeout and returns frame if available.
        """

        while not self.transaction_complete():
            time.sleep(0.01)

        return self.read_async()

    def read_waiting(self):
        """
        Alternative method for reading frame in blocking mode.
        Blocks until read timeout and returns frame if available.
        """

        if self.transceive_event.wait(timeout=self.TRANSACTION_TIMEOUT):
            return self.read_queue.get()
        raise Exception('Something went horribly wrong while communicating with Gate.')

    def write_async(self, frame):
        """
        Adds frame into outgoing messages pool.
        """

        self.transceive_event.clear()
        self.write_queue.put(frame)

    def read_async(self):
        """
        Returns last frame from incoming messages pool.
        """

        if self.read_queue.empty():
            return None
        else:
            return self.read_queue.get()

    def transaction_complete(self):
        """
        Indicates if transaction concluded.
        Can be polled for indication in non-blocking reading mode.
        """

        return self.transceive_event.is_set()

    def _comm_loop(self):
        """
        Will be executed in thread responsible for message sending.

        1. Checks if there is message in outgoing messages pool.
        2. If so, then sends it.
        3. Waits for response. Reads it using read_raw_frame.
        4. Validates response bych checking crc, functioncode and is_frame_valid.
        5. Inserts received frame to the incoming messages pool.
        """

        self.logger.debug('Communication thread started!', extra=self.log_args)
        while(self.run_thread):
            if not self.write_queue.empty():
                # Retrieve frame to send
                request_frame = self.write_queue.get()

                # Store mapping for later
                request_frame_mapping = request_frame.pdu_mapping

                # Pack and send
                request_frame.pack()
                time.sleep(self.INTERMESSAGE_DELAY)

                msg = "".join("\\0x%02x" % i for i in request_frame.raw_data)
                self.logger.debug('Sending raw request: {}'.format(msg), extra=self.log_args)

                self.write(request_frame)
                time.sleep(self.WRITE_READ_DELAY)

                # Receive response
                response_frame = self._read_raw_frame()

                msg = "".join("\\0x%02x" % i for i in response_frame.raw_data)
                self.logger.debug('Received raw response: {}'.format(msg), extra=self.log_args)

                if response_frame.raw_data:
                    response_frame.len = len(response_frame.raw_data)
                    # Check crc
                    received_crc = response_frame.raw_data[-2:]
                    computed_crc = response_frame.compute_error_check(response_frame.raw_data[0:-2]).to_bytes(2, byteorder='little')

                    msg_received_crc = "".join("\\0x%02x" % i for i in received_crc)
                    msg_computed_crc = "".join("\\0x%02x" % i for i in computed_crc)

                    if (received_crc == computed_crc):
                        # CRC ok, read functioncode
                        response_fc = response_frame.raw_data[1]

                        # Test if regular or exception
                        if response_fc & 0x80:
                            self.logger.debug('Exception detected.', extra=self.log_args)
                            pdu = ExceptionResponse()
                            response_frame.exception = True
                        else:
                            if response_fc == request_frame_mapping['function_code']:
                                pdu = request_frame_mapping['response']()
                                self.logger.debug('Using mapping of request.', extra=self.log_args)
                            elif self.get_mapping_from_fc(response_fc) is not None:
                                mapping = self.get_mapping_from_fc(response_fc)
                                pdu = mapping['response']()
                                self.logger.debug('Using custom or default mapping.', extra=self.log_args)
                            else:
                                self.logger.warning('No usable mapping for response.', extra=self.log_args)

                        if pdu is not None:
                            response_frame.change_pdu_type(pdu)

                            try:
                                response_frame.unpack()
                                response_frame.valid = True

                                if (request_frame.mba == response_frame.mba
                                    and (request_frame.pdu.function_code == response_frame.pdu.function_code
                                         or response_frame.pdu.function_code == request_frame.pdu.function_code|0x80)):

                                    response_frame.direct_response = True

                            except:
                                self.logger.warning('Error during frame unpacking.', extra=self.log_args)
                        else:
                            self.logger.warning('Could not determine response pdu format.', extra=self.log_args)

                    else:
                        self.logger.warning('CRC mismatch! Received: {}, Computed: {}'.format(msg_received_crc, msg_computed_crc), extra=self.log_args)
                else:
                    self.logger.debug('Received no data.', extra=self.log_args)

                self.read_queue.put(response_frame)
                self.transceive_event.set()
            time.sleep(self.COMM_LOOP_DELAY)

    def _print_response_info(self, frame):
        """
        Helper methot that prints response frame info in readable format.
        """
        msg = str('RESPONSE: ')
        msg += self.__frame_to_str(frame)

        if frame.exception:
            self.logger.warning('{}'.format(msg), extra=self.log_args)
            self.logger.warning('Received Exception Code: {}'.format(frame.pdu.exception_code), extra=self.log_args)
        else:
            self.logger.debug('{}'.format(msg), extra=self.log_args)

    def _print_request_info(self, frame):
        """
        Helper methot that prints request frame info in readable format.
        """

        msg = str('REQUEST: ')
        msg += self.__frame_to_str(frame)

        self.logger.debug('{}'.format(msg), extra=self.log_args)

    def __frame_to_str(self, frame):
        msg = str('')
        for attr in frame.get_packable_attributes_with_names(True):
            if attr[0] == 'pdu':
                for attr in frame.pdu.get_packable_attributes_with_names(True):
                    msg += str('\t{}: {}'.format(attr[0], attr[1].value_))
            else:
                msg += str('\t{}: {}'.format(attr[0], attr[1].value_))
        return msg

    def _print_raw_response(self, frame):
        """
        Helper methot that prints raw_data. Correctly displays all bytes.
        """

        msg = str('RESPONSE: Len: {}, Data: '.format(len(frame.raw_data)))
        msg += ''.join("\\0x%02x" % i for i in frame.raw_data)
        self.logger.debug('{}'.format(msg), extra=self.log_args)

    def default_use_default_mappings(self, value):
        self.use_default_mappings = value
        if not self.use_default_mappings:
            self.default_pdu_mappings = None
        return True

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.cleware_communicable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements communication with Cleware devices, using HID.

    :copyright: 2020 Bender Robotics
"""

import hid
import time

from brest.communication import HIDCommunicable

class ClewareCommunicable(HIDCommunicable):
    """
    Represent communication with Cleware devices using HID.

    As Cleware devices does not have unique hid serial number and introduce their own variant,
    real serial number needs to be obtain by communication with device.

    :param params: Construction parameters
    :type params: dict
    """

    TYPE = 'cleware'
    CLEWARE_VID = 0x0d50
    CLEWARE_SWITCH = 0x0008
    SN_TIMEOUT = 0.4  # 0.4s, choose carefully may be hit often even for correct behavior

    def __init__(self, params):
        HIDCommunicable.__init__(self, params)

    def get_connections(self):
        return hid.enumerate(vendor_id=self.CLEWARE_VID, product_id=self.CLEWARE_SWITCH)

    def extra_probe(self, interface, device):
        """
        Probes the Cleware switch for correct serial number.

        :param device: HID device dict
        :type  device: dict
        :returns: HID device dict with correct serial number
        :rtype: dict
        """

        if not device['vendor_id'] == self.CLEWARE_VID or not device['product_id'] == self.CLEWARE_SWITCH:
            return

        sn_timeout = interface['sn_timeout'] if 'sn_timeout' in interface else self.SN_TIMEOUT

        h = hid.device()
        h.open_path(device['path'])

        try:
            old_data = h.read(6)
            raw_serial_number = []

            for i in range(8, 15):
                h.write([0x00, 0x02, i, 0x00])

                timeout = time.time() + sn_timeout
                while True:
                    new_data = h.read(6)
                    # check for timeout is needed as first number may not change and still be correct
                    if new_data[5] != old_data[5] or time.time() > timeout:
                        old_data = new_data
                        raw_serial_number.append(new_data[5])
                        break
                    else:
                        time.sleep(0.001)
            # convert ascii hex array to number
            device['serial_number'] = str(int(bytearray(raw_serial_number), 16))
        except Exception:
            self.logger.warning('Getting cleware switch serial number failed', extra=self.log_args)
        finally:
            h.close()

        return device

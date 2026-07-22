#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.supplies.models
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements identification string parsing methods for various power supply models
    based on their communication interface.

    :copyright: 2026 Bender Robotics
"""

from brest.supplies import Supplies


class SCPIModel(Supplies.Model):
    """
    SCPI-based model.
    """

    def detect(self, response: str) -> bool:
        """
        Detects if the model matches the response.

        :param response: Response from the device
        :type  response: str
        :return: True if the model matches the response, False otherwise
        :rtype: bool
        """
        if not response:
            return False

        return self.idn.lower() in response.replace(',', ' ').lower()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.supplies.models
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements identification string parsing methods for various power supply models.

    :copyright: 2026 Bender Robotics
"""

from brest.supplies import Supplies

class TenmaModel(Supplies.Model):
    def detect(self, response: str) -> bool:
        # Old Tenmas returns INFO as comma seperated string
        splitted = response.split(',')
        psu_idn = splitted[0]
        if len(splitted) == 1:
            # New Tenmas returns INFO as space separated string
            splitted = psu_idn.split(' ')
            if len(splitted) == 1:
                return False # incorrect format
        psu_idn = ' '.join(splitted[:2])    

        return self.idn.lower() in psu_idn.lower()

class MulticompModel(Supplies.Model):
    def detect(self, response: str) -> bool:
        splitted = response.split(',')
        psu_idn = splitted[0]
        if len(splitted) == 1:
            splitted = psu_idn.split(' ')
            if len(splitted) == 1:
                return False # incorrect format
        psu_idn = ' '.join(splitted[:3])    

        return self.idn.lower() in psu_idn.lower()
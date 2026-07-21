#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.loads.models
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements identification string parsing methods for various load models.

    :copyright: 2026 Bender Robotics
"""

from brest.loads import Loads


class SCPIModel(Loads.Model):
    def detect(self, response: str) -> bool:
        # Old Tenmas returns INFO as comma seperated string
        if not response:
            return False

        return self.idn.lower() in response.replace(',', ' ').lower()

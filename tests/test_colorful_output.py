#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.tests.test_colorful_output
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module performs test print for user to verify it is colorful.

    :copyright: 2024 Bender Robotics
"""

import logging
import brest

def test_display_colorful_logs():
    l = logging.getLogger('brest')
    # Use a dict for extra to avoid manual attribute errors if formatting fails
    la = {'class_name': 'ColorTest'} 
    
    print("\n--- VISUAL CHECK: COLORS SHOULD APPEAR BELOW ---")
    l.error('This should be RED/BOLD', extra=la)
    l.warning('This should be YELLOW', extra=la)
    l.info('This should be WHITE/CYAN', extra=la)
    l.debug('This should be DIM/GREY', extra=la)
    print("--- END VISUAL CHECK ---\n")
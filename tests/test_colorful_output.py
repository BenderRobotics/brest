# -*- coding: utf-8 -*-
"""
    brest.tests.test_colorful_output
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module performs test print for user to verify it is colorful.

    :copyright: 2020 Bender Robotics
"""

import os
import sys
import logging

sys.path.insert(0, os.path.abspath('..'))
import brest

l = logging.getLogger('brest')
la = {'class_name': __name__}
l.error('Log message', extra=la)
l.warning('Log message', extra=la)
l.info('Log message', extra=la)
l.debug('Log message', extra=la)

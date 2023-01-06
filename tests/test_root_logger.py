#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.tests.test_root_logger
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module checks for brest log formatter leaking into root logger.
    Inspired by bug report #3802.

    There was a logger created by brest named 'root'.
    In Python 3.9 creating such logger would in fact overwrite settings of root logger.
    The setting in brest includes custom formatting variable 'class_name' that is naturally not present in other packages.
    This caused the Python 3.9 fail upon logging after importing brest.
    This test aims at verifying that such faulty behavior is not present in further releases.

    The test logs its behavior without using logging module as that is effectively the module under test.

    :copyright: 2023 Bender Robotics
"""

import os
import sys
import logging

sys.path.insert(0, os.path.abspath('..'))

import brest

msg = (
    '\r\n   There are no try/except attempts in this test' +
    '\r\n       On different Python versions different levels of failures were observed.' +
    '\r\n   There is no logging used for the purpose of log creation.' +
    '\r\n       The logging module is the module under test.' +
    '\r\n   This test either passes or throws an exception.' +
    '\r\n   The script tests 2 loggers: root logger and logger called "root".' +
    '\r\n   (Inspired by bug report #3802)'
)

print('\r\n'.ljust(82, '='))
print('TEST ROOT LOGGER%s' % msg)
print('\r\n'.rjust(82, '='))

logger = logging.getLogger()
logger.info('ping')
print('INFO: Root logger OK.')

logger = logging.getLogger('root')
logger.info('ping')
print('INFO: Logger called "root" OK.')

print('\r\n'.ljust(82, '='))
print('TEST ROOT LOGGER - OK')
print('\r\n'.rjust(82, '='))

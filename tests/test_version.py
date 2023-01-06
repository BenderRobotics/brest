#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.tests.test_version
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This module performs version test.

    :copyright: 2023 Bender Robotics
"""

import os
import brest

curr_ver = brest.__version__
exp_ver = os.environ['CI_COMMIT_TAG']

msg = 'Version mismatch! (Current={0} != Expected={1})'.format(curr_ver, exp_ver)
assert curr_ver == exp_ver, msg

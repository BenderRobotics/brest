#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.cameras.generic_camera
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements controling camera using OpenCV.

    :copyright: 2020 Bender Robotics
"""

import logging

from brest.cameras import Cameras
from brest.communication import CameraCommunicable


class GenericCamera(Cameras, CameraCommunicable):
    """
    OpenCV operable camera.

    Derived from: :class:`~brest.cameras.Cameras`, :class:`~brest.communication.CameraCommunicable`

    :param params: Construction parameters
    :type  params: dict
    """

    Cameras.KNOWN['GenericCamera'] = {
        'type': 'camera',
        'service': 'usbvideo',
        }

    def __init__(self, params):
        Cameras.__init__(self, params)
        CameraCommunicable.__init__(self, params['interface'])

        try:
            import cv2
        except ModuleNotFoundError:
            raise ModuleNotFoundError('To use {} class you have to install `opencv-python` module'.format(self.__class__.__name__))

        self._cam = cv2.VideoCapture(params['interface']['index'])
        self.acquire_images()

    def __del__(self):
        self.release()

    def release(self):
        Cameras.release(self)
        CameraCommunicable.release(self)

        if self._cam is not None:
            self._cam.release()
            del self._cam

    def acquire_image(self):
        return self.cam.read()[1]

    def detect_model(self):
        pass

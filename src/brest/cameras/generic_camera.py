#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.cameras.generic_camera
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements controling camera using OpenCV.

    :copyright: 2024 Bender Robotics
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
            raise ModuleNotFoundError(
                'To use {} class you have to install `opencv-python` module'.format(self.__class__.__name__)
            )

        cv_api = cv2.CAP_ANY
        if 'cv_api' in params['interface']:
            cv_api = self._process_cv_api(params['interface']['cv_api'])

        self._cam = cv2.VideoCapture(params['interface']['index'], cv_api)
        self.acquire_images()

    def __del__(self):
        self.release()

    def release(self):
        Cameras.release(self)
        CameraCommunicable.release(self)

        if self._cam is not None:
            self._cam.release()
            # Delete to ensure memory clearance and recreate variable for further functionality
            del self._cam
            self._cam = None

    def acquire_image(self):
        return self.cam.read()[1]

    def detect_model(self):
        pass

    def _process_cv_api(self, api_param):
        try:
            import cv2
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                'To use {} class you have to install `opencv-python` module'.format(self.__class__.__name__)
            )

        cv_api = cv2.CAP_ANY  # Default value
        if isinstance(api_param, int):
            cv_api = api_param
        elif isinstance(api_param, str):
            try:
                eval_str = 'cv2.' + api_param
                cv_api = eval(eval_str)
            except Exception as ex:
                self.logger.warning('Exception while determining CV API from string:\n{}'.format(ex),
                                    extra=self.log_args)
        else:
            msg = 'CV API parameter {} (type {}) is not supported'.format(api_param, type(api_param))
            msg += ', try int or str. Continuing with default value {}'.format(cv_api)
            self.logger.warning(msg, extra=self.log_args)
        return cv_api

# -*- coding: utf-8 -*-
"""
    brest.helpers
    ~~~~~~~~~~~~~

    This module implements base abstract class for cameras.

    :copyright: 2019 Bender Robotics
"""

import time

from brest import Resource


class Cameras(Resource):
    """
    Base abstract class for representing a camera.
    """

    KNOWN = {}

    def __init__(self, params=None):
        Resource.__init__(self, params)
        self._cam = None
        self.img_width = 0
        self.img_height = 0

    @property
    def cam(self):
        """
        Camera interface reference.
        """

        return self._cam

    @property
    def resolution(self):
        """
        Camera image resolution in pixels (width, height).
        """

        return (self.img_width, self.img_height)

    def acquire_image(self):
        """
        Acquire an image from the camara.
        """

        raise NotImplementedError('This camera has no meas of image acquisition')

    def acquire_images(self, num_images=1, period=0):
        """
        Acquire a returns one or more images in a list.

        :param num_images: number of images to acquire
        :type  num_images: int
        :param period: delay in between acquisition of two images in [s]
        :type period: float
        :return: list of images
        """

        frames = []

        for _ in range(int(num_images)):
            tic = time.time()
            frames.append(self.acquire_image())

            if period > 0:
                pause = max(0, period - (time.time() - tic))
                time.sleep(pause)

        return frames

    def reset_trigger(self):
        """
        Turn off camera trigger.
        """

        raise NotImplementedError('This camera doesn\'t support trigger')

    def get_info(self):
        """
        Returns info string.
        """

        raise NotImplementedError('This camera has no means of info detection.')

    def detect_model(self):
        """
        Returns model info. Implicitly tries to apply model's limits and specifications.
        """

        raise NotImplementedError('This supply does not support specific model detection.')

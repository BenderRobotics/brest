import logging

from brest.cameras import Cameras
from brest.communication import CameraCommunicable

class GenericCamera(Cameras, CameraCommunicable):

    Cameras.KNOWN['GenericCamera'] = {
        'type': 'camera',
        'lib': 'cv2'
        }

    def __init__(self, kwargs):
        Cameras.__init__(self)
        CameraCommunicable.__init__(self, kwargs['interface'])

        try:
            import cv2
        except ModuleNotFoundError:
            raise ModuleNotFoundError('To use {} class you have to install `opencv-python` module'.format(self.__class__.__name__))

        self._cam = cv2.VideoCapture(kwargs['interface']['index'])
        self.acquire_images()
        self.mark_taken(self)

    def __del__(self):
        if self.cam:
            self.cam.release()
        self.unmark_taken(self)

    def acquire_image(self):
        return self.cam.read()[1]

    def acquire_images(self, num_images = 1):
        frames = []

        for _ in range(num_images):
            frames.append(self.acquire_image())

        return frames

    def detect_model(self):
        pass

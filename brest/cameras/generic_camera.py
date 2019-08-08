from brest.cameras import Cameras

class GenericCamera(Cameras):

    Cameras.KNOWN['GenericCamera'] = {'type': 'camera'}

    def __init__(self, kwargs):
        Cameras.__init__(self)
        self.parse_args(kwargs)
        import cv2
        self._cam = cv2.VideoCapture(kwargs['interface']['index'])
        self.acquire_images()

    def __del__(self):
        self.cam.release()

    def acquire_image(self):
        return self.cam.read()[1]

    def acquire_images(self, num_images = 1):
        frames = []

        for _ in range(num_images):
            frames.append(self.acquire_image())

        return frames
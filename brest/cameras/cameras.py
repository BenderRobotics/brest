from brest import Resource

class Cameras(Resource):

    KNOWN = {}

    def __init__(self, params = None):
        Resource.__init__(self, params)
        self._cam = None

    @property
    def cam(self):
        return self._cam

    def acquire_image(self):
        '''
        Acquire an image
        '''

        raise NotImplementedError('This camera has no meas of image acquisition')

    def acquire_images(self, num_images = 1):
        '''
        Acquire a returns one or more images in a list.
        '''

        raise NotImplementedError('This camera has no means of image acquisition')

    def reset_trigger(self):
        '''
        Turn of camera trigger.
        '''

        raise NotImplementedError('This camera doesn\'t support trigger')

    def get_info(self):
        '''
        Returns info string.
        '''

        raise NotImplementedError('This camera has no means of info detection.')

    def detect_model(self):
        """Returns model info. Implicitly tries to apply model's limits and specifications."""

        raise NotImplementedError('This supply does not support specific model detection.')

import logging

class Resource():
    '''
    Base class for representing resource by name.
    '''

    cnt = 0

    def __init__(self):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')
        
        self.name = 'resource_' + str(Resource.cnt)
        Resource.cnt += 1

    def parse_args(self, kwargs):
        '''
        If object has attribute specified in `kwargs` dict, sets its value.
        '''

        for attr, value in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                if attr != 'interface':
                    self.logger.warning('Class `{}` don\'t have `{attr}` attribute'.format(self.__class__.__name__), extra=self.log_args)
import logging

class Resource():
    '''
    Base class for representing resource by name.
    '''

    cnt = 0

    def __init__(self):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')
        
        self.__name = 'resource_' + str(Resource.cnt)
        Resource.cnt += 1

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    def parse_args(self, kwargs):
        '''
        If object has attribute specified in `kwargs` dict, sets its value.
        '''

        for attr, value in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                pass #TODO: Inform user about non existing attribute
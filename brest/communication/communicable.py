class Communicable():
    '''
    Base class for communication interfaces.
    '''

    def connect(self, **kwargs):
        '''
        Tries to connect to the interface.
        '''

        raise NotImplementedError('This interface doesn\'t support connection')

    def disconnect(self):
        '''
        Tries to disconnect from the interface.
        '''

        raise NotImplementedError('This interface doesn\'t support disconnection')

    def trancieve(self, command, value = None):
        '''
        Sends and receives message in blocking mode.
        '''

        raise NotImplementedError('This interface doesn\'t support trancieve communication')

    def send_command_async(self, command, modifire = None, callback = None):
        '''
        Sends message in non-blocking mode and pass the received message to the callback
        '''

        raise NotImplementedError('This interface doesn\'t support async communication')
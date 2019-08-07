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

    def check_connecion(self):
        '''
        Checks if connection is able to send a receive messages.
        '''

        raise NotImplementedError('This interface doesn\'t implement connection check')

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

    class Handler():
        '''
        Base class for interface creation and probing.
        '''

        def is_taken(self, interface, taken):
            raise NotImplementedError('is_taken not implemented')

        def probe(self, resource, coms = None):
            raise NotImplementedError('probe not implemented')

        def available(self, class_name, interface):
            raise NotImplementedError('available not implemented')

        def complete_interface(self, interface, connected):
            raise NotImplementedError('complete_interface not implemented')

        def find_class(self, interface):
            raise NotImplementedError('find_class_by_interface not implemented')
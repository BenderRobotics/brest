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

        def mark_taken(self, interface):
            raise NotImplementedError('mark_taken is not implemented')

        def is_taken(self, interface):
            raise NotImplementedError('is_taken is not implemented')

        def probe(self, interface, coms = None):
            raise NotImplementedError('probe is not implemented')

        def get_available(self, class_name, interface, connected):
            raise NotImplementedError('available is not implemented')

        def complete_interface(self, params, connected):
            raise NotImplementedError('complete_interface is not implemented')

        def match_interface(self, interface, known_interface):
            raise NotImplementedError('find_class_by_interface is not implemented')
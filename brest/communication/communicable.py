class CommunicableError(Exception):
    '''
    Exception representing an error during communication.
    '''

    pass

class Communicable():
    '''
    Base class for communication interfaces.
    '''

    def connect(self):
        '''
        Tries to connect to the interface.
        '''

        raise NotImplementedError('This interface doesn\'t implement connection')

    def disconnect(self):
        '''
        Tries to disconnect from the interface.
        '''

        raise NotImplementedError('This interface doesn\'t implement disconnection')

    def check_connection(self):
        '''
        Checks if connection is able to send a receive messages.
        '''

        raise NotImplementedError('This interface doesn\'t implement connection check')

    def write_raw(self, data):
        '''
        Writes bytes like object directly into the connection.
        '''

        raise NotImplementedError('This interface doesn\'t implement raw data writing')

    def read_raw(self, expected='', size = None):
        '''
        Reads directly from the connection and returs bytes like object.
        '''

        raise NotImplementedError('This interface doesn\'t implement raw data reading')

    def write(self, message):
        '''
        Accepts CommunicalbeStructure as a message. Sends message in a blocking mode. Should use write_raw to send the message.
        '''

        raise NotImplementedError('This interface doesn\'t implement message write')

    def transceive(self, message):
        '''
        Accepts CommunicalbeStructure as a message. Sends and receives message in a blocking mode.  Should use write_raw, read_raw to send and receive the message.
        '''

        raise NotImplementedError('This interface doesn\'t implement transceive communication')

    def write_async(self, message):
        '''
        Accepts CommunicalbeStructure as a message. Sends message in a non-blocking mode. Should use write_raw to send the message.
        '''

        raise NotImplementedError('This interface doesn\'t implement message write')

    def transceive_async(self, message):
        '''
        Accepts CommunicalbeStructure as a message. Sends and receives message in a non-blocking mode.  Should use write_raw, read_raw to send and receive the message.
        '''

        raise NotImplementedError('This interface doesn\'t implement transceive communication')

    class Seeker():
        '''
        Base class for interface creation and probing.
        '''

        def mark_taken(self, interface):
            '''
            Marks given interface as taken. Such interface won't be listed or used again.
            '''

            raise NotImplementedError('This seeker doesn\'t implement taken interface marking')

        def is_taken(self, interface):
            '''
            Returs if given interface is taken or not.
            '''

            raise NotImplementedError('This seeker doesn\'t implement taken checking')

        def print_probe(self, interface, coms = None):
            '''
            Prints available connection nodes for given interface
            '''

            raise NotImplementedError('This seeker doesn\'t implement printing probe')

        def get_available(self, class_name, interface, connected):
            '''
            Returns list of parameter for resources, that can be constructed.
            '''

            raise NotImplementedError('This seeker doesn\'t implement listing available resources')

        def complete_interface(self, interface, connected):
            '''
            Tries to complete missing interface parameters. Raises LookupError when fails.
            '''

            raise NotImplementedError('This seeker doesn\'t implement interface completion')

        def match_interface(self, interface, known_interface):
            '''
            This method indicates interface equality. Returs True if interfaces match, return False othervise.
            '''

            raise NotImplementedError('This seeker doesn\'t implement interface matching')
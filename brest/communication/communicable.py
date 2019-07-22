class Communicable():
    
    def connect(self, **kwargs):
        raise NotImplementedError('This device doesn\'t support connection')

    def disconnect(self):
        raise NotImplementedError('This device doesn\'t support disconnection')

    def trancieve(self, command, modifier = None):
        raise NotImplementedError('This device doesn\'t support trancieve communication')

    def send_command_async(self, command, modifire = None, callback = None):
        raise NotImplementedError('This device doesn\'t support async communication')
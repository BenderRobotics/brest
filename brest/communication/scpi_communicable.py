from brest.communication import SerialCommunicable, CommunicationStructure
from brest.communication.types import str_t

class SCPICommunicable(SerialCommunicable):
    """Class that represent communication using SCPI commands.

    Derived from: :class:`~brest.communication.SerialCommunicable`
    """

    ENCODING = 'utf-8'
    SUFFIXES = [
        '',
        '\n',
    ]

    def __init__(self, kwargs):
        SerialCommunicable.__init__(self, kwargs)

        self.message_suffix = self.SUFFIXES[0] #TODO: Don't forget to mention in the documentation

    def determine_suffix(self, command):
        """Tries to determine communication messages suffix.

        Given command should return any string response in any state of
        device. Function will interate over available suffixes until
        given command returns string.
        :param command: Command which should return any string response.
        :type  command: :class:`~brest.communication.SCPICommand`
        """

        i = 0
        response = self.transceive(command)
        while not response:
            i += 1
            if i == len(self.SUFFIXES):
                raise LookupError('Can\'t find a suitable message suffix')
            self.message_suffix = self.SUFFIXES[i]
            response = self.transceive(command)

    def write(self, message):
        """Sends a message in a blocking mode.

        :param message: Message to be sent
        :type  message: :class:`~brest.communication.SCPICommand` or :class:`~brest.communication.SCPIValueCommand`
        """

        message.pack()
        data = bytearray(message.raw_data)
        if self.message_suffix:
            data += self.message_suffix.encode(self.ENCODING)
        self.write_raw(data)

    def transceive(self, message):
        """Sends and receive a message in a blocking mode.

        :param message: Message to be sent
        :type  message: :class:`~brest.communication.SCPICommand` or :class:`~brest.communication.SCPIValueCommand`
        :return: Message from a device
        :rtype: str
        """

        self.write(message)
        received = self.read_raw(expected=self.message_suffix)
        return received.decode(self.ENCODING)

class SCPICommand(CommunicationStructure):
    """Class that wraps plaintext commands

    :param command: Plaintext command you want to send
    :type  command: str
    :param channel: Number of channel if device is multichannel
    :type  channel: int
    """

    def __init__(self, command, channel = ''):
        CommunicationStructure.__init__(self)
        self.add('cmd', str_t(command))
        self.add('channel', str_t(channel))

class SCPIQueryCommand(SCPICommand):
    """Class that wraps plaintext commands adding a query character

    :param command: Plaintext command you want to send
    :type  command: str
    :param channel: Number of channel if device is multichannel
    :type  channel: int
    """

    def __init__(self, command, channel = '', query_char = '?'):
        SCPICommand.__init__(self, command, channel)
        self.add('query_char', str_t(query_char))

class SCPIValueCommand(SCPICommand):
    """Class that wraps plaintext commands with additional value

    :param command: Plaintext command you want to send
    :type  command: str
    :param channel: Number of channel if device is multichannel
    :type  channel: int
    :param value: Value that is converted to string and concate
                  with leading ':'
    :type  value: any
    """

    def __init__(self, command, channel = '', value = '', delimiter = ':'):
        SCPICommand.__init__(self, command, channel)
        self.add('delimiter', str_t(delimiter))
        self.add('value', str_t(value))

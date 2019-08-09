from brest.communication import SerialCommunicable

class SCPICommunicalbe(SerialCommunicable):

    ENCODING = 'utf-8'

    def __init__(self, kwargs):
        SerialCommunicable.__init__(self, kwargs)

        self.message_suffix = '' #TODO: Dont forget to mention in the documentation

    def transceive(self, command, value = None):
        message = command.cmd

        if command.modifier_required:
            if value:
                if message[-1] == '?':
                    message = message[:-1] + ':' + str(value)
                else:
                    message = message + str(value)
            else:
                self.logger.warning('Command requires value, but value is missing. Message is not sent.', extra=self.log_args)
                return

        message += self.message_suffix
        self.com.write(message.encode(SCPICommunicalbe.ENCODING))

        if command.response_expected:
            received = ''
            while True:
                char = str(self.com.read(), SCPICommunicalbe.ENCODING)
                received += char
                if '\n' == char or char is None or '' == char:
                    break
            
            return received
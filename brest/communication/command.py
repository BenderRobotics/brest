class Command():
    '''
    Class that wraps plaintext commands, holding additional info
    '''

    def __init__(self, cmd, modifier_required, response_expected):
        self.cmd = cmd
        self.modifier_required = modifier_required
        self.response_expected = response_expected
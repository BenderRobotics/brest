from brest.communication import Communicable

class NoneCommunicable(Communicable):

    TYPE = 'none'

    def __init__(self, params):
        Communicable.__init__(self)

    def get_connections(self):
        return []

    def probe(self, interface, connections = None):
        return interface

    def mark_taken(self, interface):
        pass

    def is_taken(self, interface):
        return False

    def get_available(self, class_name, interface, connections):
        return [
            {'class_name': 'Mansup', 'interface': {'type': 'none'}},
        ]

    def print_interface(self, interface):
        for name, value in interface.items():
            print('\t{}: {}'.format(name, value))

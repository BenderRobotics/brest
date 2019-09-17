from brest.communication import Communicable

class NoneCommunicable(Communicable):

    def __init__(self):
        Communicable.__init__(self)

    class Seeker(Communicable.Seeker):

        def __init__(self):
            Communicable.Seeker.__init__(self)

        def mark_taken(self, interface):
            pass

        def is_taken(self, interface):
            return False

        def print_probe(self, interface, coms = None):
            print()

        def get_available(self, class_name, interface, connected):
            return [
                {'class_name': 'Mansup', 'interface': {'type': 'none'}},
            ]

        def complete_interface(self, interface, connected):
            return interface
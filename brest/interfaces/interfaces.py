from brest import Resource

class Interfaces(Resource):

    KNOWN = {}

    def __init__(self, params = None):
        Resource.__init__(self, params)

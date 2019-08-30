from brest import Resource

class Interfaces(Resource):

    KNOWN = {}

    def __init__(self):
        Resource.__init__(self)
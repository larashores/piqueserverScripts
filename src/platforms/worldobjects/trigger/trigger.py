class Trigger:
    type = None
    parent = None
    status = False
    unique = False
    negate = False

    def __init__(self, protocol, negate = False):
        self.protocol = protocol
        self.negate = negate

    def unbind(self):
        self.parent.triggers.remove(self)

    def get_status(self):
        return self.status ^ self.negate

    def serialize(self):
        return {'type': self.type, 'negate': self.negate}

class BaseObject:
    protocol = None
    id = None

    def __init__(self, protocol, id):
        self.protocol = protocol
        self.id = id

    def release(self):
        pass
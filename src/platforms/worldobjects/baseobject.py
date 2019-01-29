from abc import ABCMeta


class BaseObject(metaclass=ABCMeta):
    def __init__(self, protocol, id_):
        self._protocol = protocol
        self._id = id_

    def release(self):
        """Remove an object from the world"""
        pass

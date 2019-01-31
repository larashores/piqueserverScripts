from abc import abstractmethod, ABCMeta


class BaseObject(metaclass=ABCMeta):
    id = property(lambda self: self._id)

    def __init__(self, protocol, id_):
        self._protocol = protocol
        self._id = id_

    @abstractmethod
    def destroy(self):
        pass

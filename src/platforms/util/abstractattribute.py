from abc import abstractmethod, ABCMeta


abstractattribute = property(classmethod(abstractmethod(lambda cls: NotImplementedError)))

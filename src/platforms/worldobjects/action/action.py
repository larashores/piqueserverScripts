from platforms.abstractattribute import abstractattribute, abstractmethod, ABCMeta


class Action(metaclass=ABCMeta):
    NAME = abstractattribute

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

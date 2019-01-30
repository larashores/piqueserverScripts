from platforms.util.abstractattribute import abstractattribute, abstractmethod, ABCMeta


class Action(metaclass=ABCMeta):
    NAME = abstractattribute

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

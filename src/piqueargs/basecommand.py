from abc import abstractmethod, ABCMeta
from src.piqueargs.piqueargsexception import PiqueArgsException, StopParsingException


class BaseCommand(metaclass=ABCMeta):
    name = property(lambda self: self._name)
    usage = property(lambda self: self._usage)

    def __init__(self, function, usage, name=None):
        self._name = name if name is not None else function.__name__
        self._function = function
        self._usage = usage

    def __call__(self, *args, **kwargs):
        self._function(*args, **kwargs)

    @abstractmethod
    def parse_args(self, connection, args, context):
        pass

    def run(self, connection, args):
        try:
            return self.parse_args(connection, list(args), {})
        except PiqueArgsException as e:
            return e.cls.usage
        except StopParsingException as e:
            return e.msg

from src.piqueargs.basecommand import BaseCommand
from src.piqueargs.piqueargsexception import PiqueArgsException


class Command(BaseCommand):
    def __init__(self, function, usage, name):
        BaseCommand.__init__(self, function, usage, name)
        self._arguments = []

    def add_argument(self, argument):
        if any(arg.name == argument.name for arg in self._arguments):
            raise PiqueArgsException('Argument {} already exists'.join(argument.name), self)
        self._arguments.append(argument)

    def parse_args(self, connection, args, context):
        for argument in self._arguments:
            new_context = {}
            try:
                argument.parse_args(args, new_context)
            except PiqueArgsException as e:
                raise PiqueArgsException(e.msg, self)
            context.update(new_context)
        result = self._function(connection, **context)
        if args:
            raise PiqueArgsException('Done parsing {} and still args {}'.format(self, args), self)
        return result

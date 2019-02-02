from piqueparser.piqueargsexception import PiqueArgsException


class Argument:
    name = property(lambda self: self._name)

    def __init__(self, name, *, default=None, type=str, nargs=1, required=True):
        self._name = name
        self._type = type
        self._nargs = nargs
        self._required = required
        self._default = type(default) if default is not None else type()

    def parse_args(self, args, context):
        if abs(self._nargs) > len(args):
            if not self._required:
                context[self._name] = self._default
            else:
                raise PiqueArgsException('Not enough arguments!')
        else:
            if self._nargs <= 0:
                self._nargs = len(args)
            parsed_args = ' '.join(args[:self._nargs])
            try:
                context[self._name] = self._type(parsed_args)
            except ValueError as e:
                raise PiqueArgsException(e.args, self)
            for _ in range(self._nargs):
                args.pop(0)


from argparse.piqueargsexception import PiqueArgsException


class Argument:
    def __init__(self, name, *, default='', type=str, nargs=1, required=True):
        self._name = name
        self._default = type(default)
        self._type = type
        self._nargs = nargs
        self._required = required

    def parse_args(self, args, context):
        if self._nargs < 1:
            self._nargs = len(args)
        if self._nargs > len(args):
            if not self._required:
                context[self._name] = self._default
            else:
                raise PiqueArgsException('Not enough arguments!')
        else:
            parsed_args = ' '.join(args[:self._nargs])
            try:
                context[self._name] = self._type(parsed_args)
            except ValueError as e:
                raise PiqueArgsException(e.args, self)
            for _ in range(self._nargs):
                args.pop(0)


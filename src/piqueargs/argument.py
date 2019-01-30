from src.piqueargs.piqueargsexception import PiqueArgsException


class Argument:
    def __init__(self, name, *, default='', type=str, nargs=1, required=True):
        self.name = name
        self.default = type(default)
        self.type = type
        self.nargs = nargs
        self.required = required

    def parse_args(self, args, context):
        if self.nargs < 1:
            self.nargs = len(args)
        if self.nargs > len(args):
            if not self.required:
                context[self.name] = self.default
            else:
                raise PiqueArgsException('Not enough arguments!')
        else:
            parsed_args = ' '.join(args[:self.nargs])
            try:
                context[self.name] = self.type(parsed_args)
            except ValueError as e:
                raise PiqueArgsException(e.args, self)
            for _ in range(self.nargs):
                args.pop(0)


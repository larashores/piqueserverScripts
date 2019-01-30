class ArgumentError:
    pass


class Argument:
    def __init__(self, name, *, default='', type=str, nargs=1, required=False):
        self.name = name
        self.default = type(default)
        self.type = type
        self.nargs = nargs
        self.required = required

    def parse_args(self, args, context):
        if self.nargs < 1:
            self.nargs = len(args)
        if not args and not self.required:
            context.kwargs[self.name] = self.default
        else:
            parsed_args = ' '.join(args[:self.nargs])
            context.kwargs[self.name] = self.type(parsed_args)
            for _ in range(self.nargs):
                args.pop(0)


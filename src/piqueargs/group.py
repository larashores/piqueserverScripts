from src.piqueargs.context import Context


class Group:
    name = property(lambda self: self._name)

    def __init__(self, function, usage, name=None, required=None):
        self._name = name if name is not None else function.__name__
        self._function = function
        self._required = required
        self._usage = usage
        self._options = {}
        self._subgroups = {}
        self._return_args = []
        self._arguments = []

    def __call__(self, *args, **kwargs):
        self._function(*args, **kwargs)

    def _check_option_or_group(self, name):
        return name in self._subgroups or self._options

    def add_return_args(self, *args):
        self._return_args.extend(args)

    def add_option(self, name, code_name):
        if self._check_option_or_group(name):
            raise ValueError('Option or group {} already exists'.format(name))
        if code_name in self._options.values():
            raise ValueError('Option codename {} already exists'.format(code_name))
        self._options[name] = code_name

    def add_argument(self, argument):
        self._arguments.append(argument)

    def group(self, usage='', name=None, required=None):
        def decorator(function):
            group = Group(function, usage, name, required)
            self._subgroups[group.name] = group
            return group
        return decorator

    def parse_args(self, connection, args, context):
        for option in self._options:
            context.kwargs[self._options[option]] = False
        if args and args[0] in self._options:
            option = args.pop(0)
            context.kwargs[self._options[option]] = True

        for argument in self._arguments:
            new_context = Context()
            argument.parse_args(args, new_context)
            context.kwargs.update(new_context.kwargs)

        if self._required is not None:
            context.kwargs['end'] = (len(args) == 0)

        result = self._function(connection, **context.kwargs)
        if not args:
            return result

        new_context = Context()
        if self._return_args:
            if not isinstance(result, tuple):
                result = [result]
            new_context.kwargs.update(dict(zip(self._return_args, result)))
        command = args.pop(0)
        print('command', command)
        if command in self._subgroups:
            return self._subgroups[command].parse_args(connection, args, new_context)
        print('here')
        return self._usage

    def run(self, connection, args):
        return self.parse_args(connection, args, Context())

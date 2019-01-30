from argparse.basecommand import BaseCommand
from argparse.command import Command
from argparse.piqueargsexception import PiqueArgsException


class Group(BaseCommand):
    def __init__(self, function, usage, name=None, required=None):
        BaseCommand.__init__(self, function, usage, name)
        self._required = required
        self._options = {}
        self._subgroups = {}
        self._return_args = []

    def group(self, usage='', name=None, required=None):
        def decorator(function):
            group = Group(function, usage, name, required)
            self.add_group(group)
            return group
        return decorator

    def command(self, usage='', name=None):
        def decorator(function):
            cmd = Command(function, usage, name)
            self.add_command(cmd)
            return cmd
        return decorator

    def add_return_args(self, *args):
        if any(arg in self._return_args for arg in args):
            raise PiqueArgsException('Duplicate return args', self)
        self._return_args.extend(args)

    def add_option(self, name, code_name):
        if name in self._options:
            raise PiqueArgsException('Option {} already exists'.format(name), self)
        if code_name in self._options.values():
            raise PiqueArgsException('Option code_name {} already exists'.format(code_name), self)
        if name in self._subgroups:
            raise PiqueArgsException('Option {} already exists as group'.format(name), self)
        self._options[name] = code_name

    def add_group(self, group):
        if group.name in self._subgroups:
            raise PiqueArgsException('Group {} already exits'.format(group.name), self)
        self._subgroups[group.name] = group

    def add_command(self, command):
        if command.name in self._subgroups:
            raise PiqueArgsException('Command {} already exits'.format(command.name), self)
        self._subgroups[command.name] = command

    def parse_args(self, connection, args, context):
        for option in self._options:
            context[self._options[option]] = False
        if args and args[0] in self._options:
            option = args.pop(0)
            context[self._options[option]] = True
        if not args and self._required is not False:
            raise PiqueArgsException('Command required for group {}'.format(args), self)
        if self._required is not None:
            context['end'] = (len(args) == 0)
        result = self._function(connection, **context)
        if not args:
            return result
        else:
            new_context = {}
            if self._return_args:
                if not isinstance(result, tuple):
                    result = [result]
                new_context.update(dict(zip(self._return_args, result)))
            command = args[0]
            if command in self._subgroups:
                args.pop(0)
                result = self._subgroups[command].parse_args(connection, args, new_context)
                return result
            raise PiqueArgsException('Done parsing {} and still args {}'.format(self, args), self)

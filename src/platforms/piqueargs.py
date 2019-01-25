import click
from click.core import Command, Group, BaseCommand
from click.types import IntParamType, FloatParamType
import types
import piqueserver.commands

argument = click.argument
pass_obj = click.pass_obj


def add_server_command(func, *args, **kwargs):
    @piqueserver.commands.command(*args, **kwargs)
    def command(connection, *arg):
        return func(connection, *arg)
    return command


def group(name=None, **attrs):
    def decorator(func):
        group = click.group(name, **attrs, cls=_PiqueArgsGroup)(func)
        group.group = types.MethodType(_subgroup, group)
        group.command = types.MethodType(_subcommand, group)
        return group
    return decorator


def command(name=None, **attrs):
    def decorator(func):
        cmd = click.command(name, **attrs, cls=_PiqueArgsCommand)(func)
        return cmd
    return decorator


def option(name, argname=None):
    def decorator(func):
        func.options.append((name, name if argname is None else argname))
        return func
    return decorator


def stop_parsing(message=None):
    raise _EndEarlyException(message)


def _subgroup(self, *args, **kwargs):
    def decorator(func):
        cmd = group(*args, **kwargs)(func)
        self.add_command(cmd)
        return cmd
    return decorator


def _subcommand(self, *args, **kwargs):
    def decorator(func):
        cmd = command(*args, **kwargs)(func)
        self.add_command(cmd)
        return cmd
    return decorator


class _EndEarlyException(Exception):
    def __init__(self, text=None):
        self.message = text


class _InvokeEarlyException(Exception):
    def __init__(self, command, context):
        self.command = command
        self.context = context


class _Usage:
    def __init__(self, text, args, kwargs):
        self.text = '' if text is None else text
        self.args = [] if args is None else args
        self.kwargs = {} if kwargs is None else kwargs
        self.parent = None

    def __str__(self):
        args = []
        kwargs = {}
        current = self
        while current is not None:
            for arg in reversed(current.args):
                args.insert(0, arg)
            kwargs.update(current.kwargs)
            current = current.parent
        return self.text.format(*args, **kwargs)


class _PiqueArgsBaseCommand(BaseCommand):
    def __init__(self, *args, usage=None, usageargs=None, usagekwargs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._usage = _Usage(usage, usageargs, usagekwargs)
        self.options = []

    @property
    def usage(self):
        return str(self._usage)

    def add_parent(self, parent):
        self._usage.parent = parent._usage

    def make_context(self, info_name, args, parent=None, **extra):
        if parent is None:
            ctx = super().make_context(info_name, args, parent, **extra)
            ctx.obj = types.SimpleNamespace()
        else:
            ctx = super().make_context(info_name, args, parent, **extra)
            ctx.params['connection'] = parent.params['connection']
            ctx.obj = parent.obj

        return ctx

    def run(self, connection, args):
        try:
            ctx = self.make_context(self.name, args)
            ctx.params['connection'] = connection
            with ctx:
                result = self.invoke(ctx)
                return result
        except click.exceptions.UsageError as e:
            return e.ctx.command.usage
        except _InvokeEarlyException as e:
            e.context.params['connection'] = connection
            e.context.params['end'] = True
            try:
                return Command.invoke(e.command, e.context)
            except _EndEarlyException as e:
                return e.message
        except _EndEarlyException as e:
            return e.message


class _PiqueArgsGroup(_PiqueArgsBaseCommand, Group):
    def __init__(self, *args, required=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.required = required

    def add_command(self, cmd, name=None):
        cmd.add_parent(self)
        return super().add_command(cmd, name)

    def parse_args(self, ctx, args):
        for index in range(len(self.options)):
            option, cmd_option = self.options[index]
            if args[index] == option:
                ctx.params[cmd_option] = True
                args.pop(0)
            else:
                ctx.params[cmd_option] = False
        if not args:
            raise _InvokeEarlyException(self, ctx)
        return Group.parse_args(self, ctx, args)


class _PiqueArgsCommand(_PiqueArgsBaseCommand, Command):
    pass


def range_class(base):
    class Range(IntParamType):
        """A parameter that works similar to :data:`click.INT` but restricts
        the value to fit into a range.  The default behavior is to fail if the
        value falls outside the range, but it can also be silently clamped
        between the two edges.

        See :ref:`ranges` for an example.
        """
        name = 'integer range'

        def __init__(self, min=None, max=None, clamp=False):
            self.min = min
            self.max = max
            self.clamp = clamp

        def convert(self, value, param, ctx):
            rv = base.convert(self, value, param, ctx)
            return Range.check_value(param.name, rv, self.min, self.max)

        @staticmethod
        def check_value(name, value, min=None, max=None, clamp=None):
            if clamp:
                if min is not None and value < min:
                    return min
                if max is not None and value > max:
                    return max
            if min is not None and value < min or max is not None and value > max:
                if min is None:
                    stop_parsing("ERROR: Maximum value of '{parameter}' is {max}".format(
                        parameter=name, max=max))
                elif max is None:
                    stop_parsing("ERROR: Minimum value of '{parameter}' is {min}".format(
                        parameter=name, min=min))
                else:
                    stop_parsing("ERROR: '{parameter}' must be in the range [{min}..{max}]".format(
                        parameter=name, min=min, max=max))
            return value

        def __repr__(self):
            return '{}Range({}, {})'.format(base, self.min, self.max)
    return Range


IntRange = range_class(IntParamType)
FloatRange = range_class(FloatParamType)

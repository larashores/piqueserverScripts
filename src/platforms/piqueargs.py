import click
from click.core import Command, Group, BaseCommand
import types

argument = click.argument
pass_obj = click.pass_obj


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


def bad_command(message):
    raise _InvalidException(message)


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


class _InvalidException(Exception):
    def __init__(self, usage=None):
        self.usage = usage


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
        ctx = super().make_context(info_name, args, parent, **extra)
        if parent is not None:
            ctx.params['connection'] = parent.params['connection']
            ctx.obj = parent.obj
        else:
            ctx.obj = types.SimpleNamespace()
        return ctx


class _PiqueArgsGroup(_PiqueArgsBaseCommand, Group):
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
        if not args and self.no_args_is_help and not ctx.resilient_parsing:
            raise _InvalidException(self.usage)
        return Group.parse_args(self, ctx, args)

    def run(self, connection, args):
        try:
            ctx = self.make_context(self.name, args)
            ctx.params['connection'] = connection
            with ctx:
                result = self.invoke(ctx)
                return result
        except _InvalidException as e:
            return e.usage
        except click.exceptions.UsageError as e:
            return e.ctx.command.usage


class _PiqueArgsCommand(_PiqueArgsBaseCommand, Command):
    pass





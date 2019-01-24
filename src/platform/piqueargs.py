import click
from click.core import Command, Group, BaseCommand
import types


def group(name=None, *, usage=None, **attrs):
    def decorator(func):
        group = click.group(name, **attrs, cls=_PyArgsGroup, usage=usage)(func)
        group.group = types.MethodType(_subgroup, group)
        group.command = types.MethodType(_subcommand, group)
        return group
    return decorator


def command(name=None, usage=None, **attrs):
    def decorator(func):
        cmd = click.command(name, **attrs, cls=_PyArgsCommand, usage=usage)(func)
        return cmd
    return decorator


def bad_command(message):
    raise InvalidException(message)


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


class InvalidException(Exception):
    def __init__(self, usage=None):
        self.usage = usage


class _PyArgsBaseCommand(BaseCommand):
    def __init__(self, *args, usage=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usage = usage

    def make_context(self, info_name, args, parent=None, **extra):
        ctx = super().make_context(info_name, args, parent, **extra)
        if parent is not None:
            ctx.params['connection'] = parent.params['connection']
        return ctx


class _PyArgsGroup(_PyArgsBaseCommand, Group):
    def parse_args(self, ctx, args):
        if not args and self.no_args_is_help and not ctx.resilient_parsing:
            raise InvalidException(self.usage)

        return Group.parse_args(self, ctx, args)

    def run(self, connection, args):
        try:
            ctx = self.make_context(self.name, args)
            ctx.params['connection'] = connection
            with ctx:
                result = self.invoke(ctx)
                return result
        except InvalidException as e:
            return e.usage
        except click.exceptions.UsageError as e:
            return e.ctx.command.usage


class _PyArgsCommand(_PyArgsBaseCommand, Command):
    pass





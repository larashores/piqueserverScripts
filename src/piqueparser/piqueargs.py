from piqueparser.group import Group
from piqueparser.command import Command
from piqueparser.argument import Argument
from piqueparser.piqueargsexception import StopParsingException

from piqueserver import commands


def add_server_command(function, *args, **kwargs):
    return commands.command(*args, **kwargs)(function)


def stop_parsing(message=None):
    raise StopParsingException(message)


def group(usage='', name=None, required=None):
    def decorator(function):
        return Group(function, usage, name, required)
    return decorator


def command(usage='', name=None):
    def decorator(function):
        return Command(function, usage, name)
    return decorator


def returns(*names):
    def decorator(group):
        group.add_return_args(*names)
        return group
    return decorator


def argument(name, *, default='', type=str, nargs=1, required=True):
    def decorator(command):
        command.add_argument(Argument(name, default=default, type=type, nargs=nargs, required=required))
        return group
    return decorator


def option(name, code_name):
    def decorator(group):
        group.add_option(name, code_name)
        return group
    return decorator

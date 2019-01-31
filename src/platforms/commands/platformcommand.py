from piqueparser import piqueargs
from piqueparser.types.range import IntRange
from platforms.commands.util import base_command
from platforms.states.platform.newplatformstate import NewPlatformState
from platforms.states.platform.platformcommandstate import *


@piqueargs.group('Usage: /platform [new name height freeze destroy last]', required=False)
def platform(connection, end=False):
    return base_command(connection, end, PlatformState, platform.usage)


@piqueargs.argument('label', required=False)
@platform.command('Usage: /platform new <label>')
def new(connection, label):
    connection.state_stack.set(NewPlatformState(label))


@piqueargs.argument('label')
@platform.command('Usage: /platform name <label>')
def name(connection, label):
    connection.state_stack.set(PlatformNameState(label))


@piqueargs.argument('height_', type=IntRange(-62, 62))
@platform.command('Usage: /platform height <height>')
def height(connection, height_):
    connection.state_stack.set(PlatformHeightState(height_))


@platform.command('Usage: /platform freeze')
def freeze(connection):
    connection.state_stack.set(PlatformFreezeState())


@platform.command('Usage: /platform destroy')
def destroy(connection):
    connection.state_stack.set(PlatformDestroyState())


@platform.command('Usage: /platform last')
def last(connection):
    state = connection.state_stack.top()
    if state and isinstance(state, NeedsPlatformState) and connection.last_platform:
        state.select_platform(connection.last_platform)

"""
/p /platforms [command]
    Starts a new platforms or enables you to edit them by specifying a command.
    To build a platforms, put down blocks delimiting the size of the floor--
    two blocks in opposite corners is sufficient.

    Press the SNEAK key (V) while in any platforms mode to get information
    about the platforms you're looking at.  Must be holding spade tool.

    command:
        new <label>
            Starts a new platforms with a label already attached.
        name <label>
            Labels a platforms.  It's recommended you name things to avoid mistakes.
        height <height>
            Forces the platforms to grow or shrink to the specified height.
        freeze
            Freezes or unfreezes a platforms.  A frozen platforms won't move.
        destroy
            Destroys a platforms, removing all its blocks.
        last
            When you get asked to select a platforms, you can use this command
            to automatically choose the last platforms you selected or created.
"""
from platforms.util import piqueargs
from platforms.commands.util import base_command
from platforms.states.platform.newplatformstate import NewPlatformState
from platforms.states.platform.platformcommandstate import *


@piqueargs.group(usage='Usage: /platform [new name height freeze destroy last]', required=False)
def platform(connection, end=False):
    return base_command(connection, end, PlatformState, platform.usage)


@piqueargs.argument('label', required=False)
@platform.command(usage='Usage: /platform new <label>')
def new(connection, label):
    connection.state_stack.set(NewPlatformState(label))


@piqueargs.argument('label')
@platform.command(usage='Usage: /platform name <label>')
def name(connection, label):
    connection.state_stack.set(PlatformNameState(label))


@piqueargs.argument('height_', type=piqueargs.IntRange(1, 63))
@platform.command(usage='Usage: /platform height <height>')
def height(connection, height_):
    connection.state_stack.set(PlatformHeightState(height_))


@platform.command(usage='Usage: /platform freeze')
def freeze(connection):
    connection.state_stack.set(PlatformFreezeState())


@platform.command(usage='Usage: /platform destroy')
def destroy(connection):
    connection.state_stack.set(PlatformDestroyState())


@platform.command(usage='Usage: /platform last')
def last(connection):
    state = connection.state_stack.top()
    if state and isinstance(state, NeedsPlatformState) and connection.last_platform:
        state.select_platform(connection.last_platform)

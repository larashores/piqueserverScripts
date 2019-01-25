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
from platforms import piqueargs
from platforms.strings import S_EXIT_BLOCKING_STATE
from platforms.states.newplatformstate import NewPlatformState
from platforms.states.selectplatformstate import SelectPlatformState
from platforms.states.platformcommandstate import PlatformCommandState


@piqueargs.group(usage='Usage: /platform [new name height freeze destroy last]', required=False)
def platform(connection, end=False):
    if not end:
        return

    if connection not in connection.protocol.players:
        raise ValueError()
    state = connection.states.top()
    if state and state.get_parent().name in ('new platforms', 'platforms command'):
        connection.states.exit()  # cancel platform creation
    elif state and state.blocking:
        return S_EXIT_BLOCKING_STATE.format(state=state.name)  # can't switch from a blocking mode
    else:
        connection.states.exit()
        connection.states.enter(NewPlatformState())


@piqueargs.argument('label')
@platform.command(usage='Usage: /platform new <label>')
def new(connection, label):
    connection.states.exit()
    connection.states.enter(NewPlatformState(label))


@piqueargs.argument('label')
@platform.command(usage='Usage: /platform name <label>')
def name(connection, label):
    state = PlatformCommandState('name')
    state.label = label
    push_state(connection, state)


@piqueargs.argument('height', type=piqueargs.IntRange(0, 63))
@platform.command(usage='Usage: /platform height <height>')
def height(connection, height):
    state = PlatformCommandState('height')
    state.height = height
    push_state(connection, state)


@platform.command(usage='Usage: /platform freeze')
def freeze(connection):
    push_state(connection, PlatformCommandState('freeze'))


@platform.command(usage='Usage: /platform destroy')
def destroy(connection):
    push_state(connection, PlatformCommandState('destroy'))


@platform.command(usage='Usage: /platform last')
def last(connection):
    state = connection.states.top()
    if state and state.name == 'select platforms' and connection.previous_platform:
        state.platform = connection.previous_platform
        connection.states.pop()
    else:
        push_state(connection, PlatformCommandState('last'))


def push_state(player, state):
    player.states.exit()
    player.states.push(state)
    player.states.enter(SelectPlatformState(state))

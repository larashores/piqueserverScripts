"""
/b /button [command]
    Starts button creation. Just build a block with the desired color.

    A default button only has a Press trigger and no actions, so you'll need
    to make it do something with /action.

    Press the SNEAK key (V) while in any button mode to get information
    about the button you're looking at.  Must be holding spade tool.

    command:
        new <label>
            Starts button creation with a label already attached.
        name <label>
            Labels a button.  It's recommended you name things to avoid mistakes.
        toggle
            Disables or enables a button.  A disabled button does nothing.
        cooldown <seconds>
            The button will be able to be activated only once in the specified
            interval. Default is 0.5 seconds.
        destroy
            Destroys a button, removing the block.
        last
            When you get asked to select a button, you can use this command
            to automatically choose the last button you selected or created.
"""

from platforms import piqueargs
from platforms.strings import S_EXIT_BLOCKING_STATE
from platforms.states.buttoncommandstate import ButtonCommandState
from platforms.states.newbuttonstate import NewButtonState
from platforms.states.selectbuttonstate import SelectButtonState


@piqueargs.group(usage="Usage: /button [new name destroy toggle cooldown last]", required=False)
def button(connection, end=False):
    if not end:
        return

    if connection not in connection.protocol.players:
        raise ValueError()
    state = connection.states.top()
    if state and state.get_parent().name in ('new button', 'button command'):
        connection.states.exit()  # cancel button creation
    elif state and state.blocking:
        return S_EXIT_BLOCKING_STATE.format(state=state.name)  # can't switch from a blocking mode
    else:
        connection.states.exit()
        connection.states.enter(NewButtonState())


@piqueargs.argument('label')
@button.command(usage='Usage: /button new <label>')
def new(connection, label):
    connection.states.exit()
    connection.states.enter(NewButtonState(label))


@piqueargs.argument('label')
@button.command(usage='Usage: /button name <label>')
@piqueargs.pass_obj
def name(connection, label):
    state = ButtonCommandState('new')
    state.label = label
    push_command_state(connection, state)


@piqueargs.argument('seconds', type=piqueargs.FloatRange(0.1, 86400))
@button.command(usage='Usage: /button cooldown <seconds>')
def cooldown(connection, seconds):
    state = ButtonCommandState('cooldown')
    state.cooldown = seconds
    push_command_state(connection, state)


@button.command(usage='Usage: /button destroy')
def destroy(connection):
    push_command_state(connection, ButtonCommandState('destroy'))


@button.command(usage='Usage: /button last')
def last(connection):
    state = connection.states.top()
    if state and state.name == 'select button' and connection.previous_button:
        state.button = connection.previous_button
        connection.states.pop()
    else:
        push_command_state(connection, ButtonCommandState('last'))


def push_command_state(player, state):
    player.states.exit()
    player.states.push(state)
    player.states.enter(SelectButtonState(state))

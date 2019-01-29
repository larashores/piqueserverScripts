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
from platforms.states.button.buttoncommandstate import *
from platforms.states.button.newbuttonstate import NewButtonState
from platforms.states.button.selectbuttonstate import SelectButtonState


@piqueargs.group(usage="Usage: /button [new name destroy toggle cooldown last]", required=False)
def button(connection, end=False):
    if not end:
        return

    if connection not in connection.protocol.players:
        raise ValueError()
    state = connection.state_stack.top()
    if isinstance(state, (NewButtonState, ButtonCommandState)):
        connection.state_stack.clear()  # cancel button creation
        return
    elif state and state.BLOCKING:
        return S_EXIT_BLOCKING_STATE.format(state=state.name)  # can't switch from a blocking mode
    return button.usage


@piqueargs.argument('label', required=False)
@button.command(usage='Usage: /button new <label>')
def new(connection, label):
    connection.state_stack.clear()
    connection.state_stack.push(NewButtonState(label))


@piqueargs.argument('label')
@button.command(usage='Usage: /button name <label>')
def name(connection, label):
    push_command_state(connection, ButtonNameState(label))


@piqueargs.argument('seconds', type=piqueargs.FloatRange(0.1, 86400))
@button.command(usage='Usage: /button cooldown <seconds>')
def cooldown(connection, seconds):
    push_command_state(connection, ButtonCooldownState(seconds))


@button.command(usage='Usage: /button destroy')
def destroy(connection):
    push_command_state(connection, ButtonDestroyState())


@button.command(usage='Usage: /button last')
def last(connection):
    state = connection.state_stack.top()
    if state and isinstance(state, SelectButtonState) and connection.last_button:
        state.select_button(connection.last_button)
        state.signal_exit(state)


def push_command_state(player, state):
    player.state_stack.clear()
    player.state_stack.push(state, SelectButtonState(state))


if __name__ == '__main__':
    result = button.run(None, ['new'])
    print(result)

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
    connection.state_stack.set(NewButtonState(label))


@piqueargs.argument('label')
@button.command(usage='Usage: /button name <label>')
def name(connection, label):
    connection.state_stack.set(ButtonNameState(label))


@piqueargs.argument('seconds', type=piqueargs.FloatRange(0.1, 86400))
@button.command(usage='Usage: /button cooldown <seconds>')
def cooldown(connection, seconds):
    connection.state_stack.set(ButtonCooldownState(seconds))


@button.command(usage='Usage: /button destroy')
def destroy(connection):
    connection.state_stack.set(ButtonDestroyState())


@button.command(usage='Usage: /button last')
def last(connection):
    state = connection.state_stack.top()
    if state and isinstance(state, NeedsButtonState) and connection.last_button:
        state.select_button(connection.last_button)


if __name__ == '__main__':
    result = button.run(None, ['new'])
    print(result)

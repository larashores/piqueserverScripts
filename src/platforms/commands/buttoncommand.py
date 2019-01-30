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
        quiet
            Makes a button either become silent or resume playing animation and
            sound when it activates.
        destroy
            Destroys a button, removing the block.
        last
            When you get asked to select a button, you can use this command
            to automatically choose the last button you selected or created.
"""

from piqueparser import piqueargs
from piqueparser.types.range import IntRange, FloatRange
from platforms.commands.util import base_command
from platforms.states.button.buttoncommandstate import *
from platforms.states.button.newbuttonstate import NewButtonState


@piqueargs.group("Usage: /button [new name toggle cooldown quiet destroy last]", required=False)
def button(connection, end=False):
    return base_command(connection, end, ButtonState, button.usage)


@piqueargs.argument('label', required=False)
@button.command('Usage: /button new <label>')
def new(connection, label):
    connection.state_stack.set(NewButtonState(label))


@piqueargs.argument('label')
@button.command('Usage: /button name <label>')
def name(connection, label):
    connection.state_stack.set(ButtonNameState(label))


@piqueargs.argument('seconds', type=FloatRange(0.1, 60*60*24))
@button.command('Usage: /button cooldown <seconds>')
def cooldown(connection, seconds):
    connection.state_stack.set(ButtonCooldownState(seconds))


@button.command('Usage: /button destroy')
def destroy(connection):
    connection.state_stack.set(ButtonDestroyState())


@button.command('Usage: /button last')
def last(connection):
    state = connection.state_stack.top()
    if state and isinstance(state, NeedsButtonState) and connection.last_button:
        state.select_button(connection.last_button)


@button.command('Usage: /trigger quiet')
def quiet(connection):
    connection.state_stack.set(ButtonQuietState())

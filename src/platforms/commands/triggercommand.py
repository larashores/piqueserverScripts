"""
/t /trigger <command>
    Triggers are what makes a button know when to act and when not to.

    command:
        add [not] <action>
        set [not] <action>
            Adds a trigger to the button. Set deletes all previous triggers first,
            making the new trigger the only one.

            Putting 'not' before the action makes it NEGATE the output.
            If you want to make a button that activates when a player *leaves*
            a zone, you could use "/trigger set not distance 5"

            action:
                press
                    Fires when a player normally hits the button with the spade.
                distance [radius=3]
                    True when a player gets within <radius> blocks of the
                    button (note: box distance, not sphere).
                height <height>
                    True when the platforms is exactly the specified height.
        list
            Lists the triggers present in the button you select.

            Example:
            "Triggers in 'mybutton': #0 player press OR #1 player distance=5 [CHECK]"

            #0 and #1 are the trigger indexes to be used with /trigger del.
            [CHECK] means the trigger currently yields true. The player in this
            case is near the button, but hasn't pressed it.

            This button uses OR logic, meaning that EITHER of these triggers
            firing is enough to activate the button.
        del <#|all>
            Delete a single trigger in a button by specifying its index. Trigger
            indexes can be looked up by using /trigger list.

            Negative indexes can be used too: -1 is the last added trigger, -2 the
            one before that, and so on.

            Specifying 'all' instead of a number erases all the triggers.
        logic <and|or>
            "AND" will make the button activate when ALL its triggers yield true.
            "OR" will make the button activate when ANY of its triggers fire.
"""

from piqueparser import piqueargs
from piqueparser.types.range import IntRange, FloatRange
from piqueparser.types.enumarg import EnumArg
from platforms.commands.util import base_command, id_or_all
from platforms.states.trigger.triggeraddstate import *
from platforms.states.trigger.triggercommandstate import *
from platforms.worldobjects.button import LogicType


@piqueargs.group('Usage: /trigger [add set list del logic]', required=False)
def trigger(connection, end=False):
    return base_command(connection, end, TriggerState, trigger.usage)


@piqueargs.returns('clear_others', 'negate')
@piqueargs.option('not', 'notarg')
@trigger.group('Usage: /trigger add|set [not] <press distance height timer>')
def add(connection, notarg):
    return False, notarg


@piqueargs.returns('clear_others', 'negate')
@piqueargs.option('not', 'notarg')
@trigger.group('Usage: /trigger add|set [not] <press distance height timer>', name='set')
def set_(connection, notarg):
    return True, notarg


@piqueargs.command('Usage: /trigger add|set [not] press')
def press(connection, clear_others, negate):
    connection.state_stack.set(PlayerAddTriggerState(negate, clear_others, TriggerType.PRESS))


@piqueargs.argument('radius', default=3.0, type=FloatRange(1, 64), required=False)
@piqueargs.command('Usage: /trigger add|set [not] distance [radius=3]')
def distance(connection, clear_others, negate, radius):
    connection.state_stack.set(PlayerAddTriggerState(negate, clear_others, TriggerType.DISTANCE, radius))


@piqueargs.argument('height_', type=IntRange(-62, 62))
@piqueargs.command('/trigger add|set [not] height <height>')
def height(connection, clear_others, negate, height_):
    connection.state_stack.set(PlatformAddTriggerState(negate, clear_others, TriggerType.HEIGHT, height_))


@piqueargs.argument('amount', default='forever', required=False)
@piqueargs.argument('time', type=FloatRange(1.0, 60 * 60 * 24))
@piqueargs.command('/trigger add|set [not] timer <time> [amount|forever]')
def timer(connection, clear_others, negate, time, amount):
    if amount != 'forever':
        try:
            amount = IntRange.check_value('amount', int(amount), 1, 86400.0)
        except ValueError:
            piqueargs.stop_parsing(timer.usage)
    else:
        amount = None
    connection.state_stack.set(AddTriggerState(negate, clear_others, TriggerType.TIMER, time, amount))


@trigger.command('Usage: /trigger list', name='list')
def list_(connection):
    connection.state_stack.set(TriggerListState())


@piqueargs.argument('what', type=id_or_all)
@trigger.command('Usage: /trigger del <#|all>', name='del')
def delete(connection, what):
    connection.state_stack.set(TriggerDeleteState(what))


@piqueargs.argument('andor', type=EnumArg(LogicType))
@trigger.command('Usage: /trigger logic <and|or>')
def logic(connection, andor):
    connection.state_stack.set(TriggerLogicState(andor))


for command in (press, distance, height, timer):
    add.add_command(command)
    set_.add_command(command)

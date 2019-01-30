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

import click

from platforms.util import piqueargs
from platforms.commands.util import base_command
from platforms.commands.util import IDENTIFIER
from platforms.states.trigger.triggeraddstate import *
from platforms.states.trigger.triggercommandstate import *

POS_FLOAT = piqueargs.FloatRange(0.0, 64.0)


@piqueargs.group(usage='Usage: /trigger [add set list del logic]', required=False)
def trigger(connection, end=False):
    return base_command(connection, end, TriggerState, trigger.usage)


@piqueargs.option('not', 'notarg')
@trigger.group(usage='Usage: /trigger {} [not] <press distance track height>', usageargs=['add'])
@piqueargs.pass_obj
def add(obj, connection, notarg):
    obj.clear_others = False
    obj.negate = notarg


@piqueargs.option('not', 'notarg')
@trigger.group('set', usage='Usage: /trigger {} [not] <press distance track height>', usageargs=['set'])
@piqueargs.pass_obj
def set_(obj, connection, notarg):
    obj.clear_others = True
    obj.negate = notarg


@piqueargs.command(usage='Usage: /trigger {} [not] press')
@piqueargs.pass_obj
def press(obj, connection):
    connection.state_stack.set(PlayerAddTriggerState(obj.negate, obj.clear_others, TriggerType.PRESS))


@piqueargs.argument('radius', default=3.0, type=POS_FLOAT, required=False)
@piqueargs.command(usage='Usage: /trigger {} [not] distance [radius=3]')
@piqueargs.pass_obj
def distance(obj, connection, radius):
    connection.state_stack.set(PlayerAddTriggerState(obj.negate, obj.clear_others, TriggerType.DISTANCE, radius))


@piqueargs.argument('height_', type=piqueargs.IntRange(0, 62))
@piqueargs.command(usage='/trigger {} [not] height <height>')
@piqueargs.pass_obj
def height(obj, connection, height_):
    connection.state_stack.set(PlatformAddTriggerState(obj.negate, obj.clear_others, TriggerType.HEIGHT, height_))


@trigger.command('list', usage='Usage: /trigger list')
def list_(connection):
    connection.state_stack.set(TriggerListState())


@piqueargs.argument('what', type=IDENTIFIER)
@trigger.command('del', usage='Usage: /trigger del <#|all>')
def delete(connection, what):
    connection.state_stack.set(TriggerDeleteState(what))


@piqueargs.argument('andor', type=click.Choice(['and', 'or']))
@trigger.command(usage='Usage: /trigger logic <and|or>')
def logic(connection, andor):
    connection.state_stack.set(TriggerLogicState(andor))


for command in (press, distance, height):
    add.add_command(command)
    set_.add_command(command)

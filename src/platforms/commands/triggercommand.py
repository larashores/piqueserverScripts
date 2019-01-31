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
@piqueargs.argument('time', type=FloatRange(1.0, 60*60*24))
@piqueargs.command('/trigger add|set [not] timer <time> [amount|forever]')
def timer(connection, clear_others, negate, time, amount):
    if amount != 'forever':
        try:
            amount = IntRange.check_value('amount', int(amount), 1, 60*60*24)
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

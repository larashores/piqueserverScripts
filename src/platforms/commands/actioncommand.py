from piqueparser import piqueargs
from piqueparser.types.range import FloatRange, IntRange
from platforms.commands.util import base_command, id_or_all
from platforms.states.action.actionstate import ActionState
from platforms.states.action.addactionstate import PlatformAddActionState, PlayerAddActionState
from platforms.states.action.actioncommandstate import ActionListState, ActionDelState
from platforms.worldobjects.action.action import ActionType

from pyspades.constants import WEAPON_KILL, FALL_KILL


POS_FLOAT = FloatRange(0.0, 60*60*24)


@piqueargs.group('Usage: /action <add set list del>', required=False)
def action(connection, end=False):
    return base_command(connection, end, ActionState, action.usage)


@piqueargs.returns('clear_others')
@action.group('Usage: /action add|set <height raise lower elevator teleport chat damage>')
def add(connection):
    return False


@piqueargs.returns('clear_others')
@action.group('Usage: /action add|set <height raise lower elevator teleport chat damage>', name='set')
def set_(connection):
    return True


@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('height', type=IntRange(-62, 62))
@piqueargs.command('Usage: /action add|set height <height> [speed=0.15] [delay]')
def height(connection, clear_others, height, speed, delay):
    connection.state_stack.set(PlatformAddActionState(clear_others, ActionType.HEIGHT, height, speed, delay))


@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('amount', type=IntRange(1, 62))
@piqueargs.command(usage='Usage: /action add|set raise <amount> [speed=0.15] [delay]', name='raise')
def raise_(connection, clear_others, amount, speed, delay):
    connection.state_stack.set(PlatformAddActionState(clear_others, ActionType.RAISE, amount, speed, delay))


@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('amount', type=IntRange(1, 62))
@piqueargs.command('Usage: /action add|set lower <amount> [speed=0.15] [delay]')
def lower(connection, clear_others, amount, speed, delay):
    connection.state_stack.set(PlatformAddActionState(clear_others, ActionType.LOWER, lower, amount, speed, delay))


@piqueargs.argument('wait', default=3.0, type=POS_FLOAT, required=False)
@piqueargs.argument('delay', default=0.0, type=POS_FLOAT, required=False)
@piqueargs.argument('speed', default=.15, type=POS_FLOAT, required=False)
@piqueargs.argument('height', type=IntRange(-62, 62))
@piqueargs.command('Usage: /action add|set elevator <height> [speed=0.25] [delay] [wait=3.0]')
def elevator(connection, clear_others, height, speed, delay, wait):
    connection.state_stack.set(PlatformAddActionState(clear_others, ActionType.ELEVATOR,
                                                      height, speed, delay, True, wait))


@piqueargs.argument('z', type=FloatRange(0, 62), required=False)
@piqueargs.argument('y', type=FloatRange(-511, 511), required=False)
@piqueargs.argument('first')
@piqueargs.command('Usage: /action add|set teleport <x y z|where>')
def teleport(connection, clear_others, first, y, z):
    if first == 'where':
        if not connection.where_location:
            piqueargs.stop_parsing('ERROR: use /where first to remember your position')
        x, y, z = connection.where_location
        x = round(x * 2.0) / 2.0 - 0.5
        y = round(y * 2.0) / 2.0 - 0.5
        z = round(z) + 0.5
    elif y is not None and z is not None:
        try:
            x = FloatRange.check_value('x', float(first), -511.0, 511.0)
        except ValueError:
            piqueargs.stop_parsing(teleport.usage)
    else:
        piqueargs.stop_parsing(teleport.usage)
    z = max(0.5, z)

    connection.state_stack.set(PlayerAddActionState(clear_others, ActionType.TELEPORT, (x, y, z)))


@piqueargs.argument('text',  nargs=-1)
@piqueargs.command('Usage: /action add|set chat <text>')
def chat(connection, clear_others, text):
    connection.state_stack.set(PlayerAddActionState(clear_others, ActionType.CHAT, ' '.join(text)))


@piqueargs.argument('amount', type=IntRange(-100, 100))
@piqueargs.command('Usage: /action add|set damage <amount>')
def damage(connection, clear_others, amount):
    connection.state_stack.set(PlayerAddActionState(clear_others, ActionType.DAMAGE, amount,
                                                    kill_type=WEAPON_KILL if amount > 0 else FALL_KILL))


@action.command('Usage: /action list', name='list')
def list_(connection):
    connection.state_stack.set(ActionListState())


@piqueargs.argument('what', type=id_or_all)
@action.command('Usage: /action del <#|all>', name='del')
def delete(connection, what):
    connection.state_stack.set(ActionDelState(what))


for command in (height, raise_, lower, elevator, teleport, chat, damage):
    add.add_command(command)
    set_.add_command(command)

from piqueserver.commands import command, join_arguments
from platform.parseargs import parseargs
from platform.states.newbuttonstate import NewButtonState
from platform.states.buttoncommandstate import ButtonCommandState
from platform.states.selectbuttonstate import SelectButtonState
from platform.strings import *

MIN_COOLDOWN = 0.1  # seconds

BUTTON_COMMANDS = ('new', 'name', 'destroy', 'toggle', 'cooldown', 'last')
S_BUTTON_USAGE = 'Usage: /button [{commands}]'
BUTTON_COMMAND_USAGES = {
    'new': 'Usage: /button new <label>',
    'name': 'Usage: /button name <label>',
    'cooldown': 'Usage: /button cooldown <seconds>'
}


@command('button', 'b')
def button_command(connection, *args):
    protocol = connection.protocol
    if connection not in protocol.players:
        raise ValueError()
    player = connection
    state = player.states.top()

    if state:
        state_name = state.get_parent().name
        if state_name in ('new button', 'button command') and not args:
            # cancel button creation
            player.states.exit()
            return
        elif state.blocking:
            # can't switch from a blocking mode
            return S_EXIT_BLOCKING_STATE.format(state=state.name)
    if args:
        # enter new mode
        available = '|'.join(BUTTON_COMMANDS)
        usage = S_BUTTON_USAGE.format(commands=available)
        try:
            command = args[0]
            if command not in BUTTON_COMMANDS:
                return usage

            usage = BUTTON_COMMAND_USAGES.get(command, usage)
            new_state = ButtonCommandState(command)
            if command in ('new', 'name'):
                new_state.label = join_arguments(args[1:], '').strip()
                if not new_state.label:
                    return usage
            elif command == 'cooldown':
                new_state.cooldown, = parseargs('float', args[1:])
                if new_state.cooldown < 0.0:
                    message = S_NOT_POSITIVE.format(parameter='cooldown')
                    raise ValueError(message)
                if new_state.cooldown < MIN_COOLDOWN:
                    message = S_MINIMUM.format(parameter='cooldown', value=MIN_COOLDOWN)
                    raise ValueError(message)
            elif command == 'last' and state:
                if state.name == 'select button' and player.previous_button:
                    state.button = player.previous_button
                    player.states.pop()
                    return
        except ValueError as err:
            player.send_chat(usage)
            return str(err)
        except IndexError:
            return usage

        player.states.exit()
        if command == 'new':
            # start button creation with label
            player.states.enter(NewButtonState(new_state.label))
        else:
            player.states.push(new_state)
            player.states.enter(SelectButtonState(new_state))
    else:
        # start button creation
        player.states.exit()
        player.states.enter(NewButtonState())

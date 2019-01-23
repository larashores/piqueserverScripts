from piqueserver.commands import command
from platform.parseargs import parseargs

S_PLATFORM_USAGE = 'Usage: /platform [{commands}]'


@command('platform', 'p')
def platform_command(connection, *args):
    protocol = connection.protocol
    if connection not in protocol.players:
        raise ValueError()
    player = connection
    state = player.states.top()

    if state:
        state_name = state.get_parent().name
        if state_name in ('new platform', 'platform command') and not args:
            # finish platform construction
            player.states.exit()
            return
        elif state.blocking:
            # can't switch from a blocking mode
            return S_EXIT_BLOCKING_STATE.format(state = state.name)
    if args:
        # enter new mode
        available = '|'.join(PLATFORM_COMMANDS)
        usage = S_PLATFORM_USAGE.format(commands = available)
        try:
            command = args[0]
            if command not in PLATFORM_COMMANDS:
                return usage

            usage = PLATFORM_COMMAND_USAGES.get(command, usage)
            new_state = PlatformCommandState(command)
            if command == 'height':
                new_state.height, = parseargs('int', args[1:])
                if new_state.height < 0:
                    message = S_NOT_POSITIVE.format(parameter = 'height')
                    raise ValueError(message)
            elif command in ('new', 'name'):
                new_state.label = join_arguments(args[1:], '').strip()
                if not new_state.label:
                    return usage
            elif command == 'last' and state:
                if state.name == 'select platform' and player.previous_platform:
                    state.platform = player.previous_platform
                    player.states.pop()
                    return
        except ValueError as err:
            player.send_chat(usage)
            return str(err)
        except IndexError:
            return usage

        player.states.exit()
        if command == 'new':
            # start construction with label
            player.states.enter(NewPlatformState(new_state.label))
        else:
            player.states.push(new_state)
            player.states.enter(SelectPlatformState(new_state))
    else:
        # start construction
        player.states.exit()
        player.states.enter(NewPlatformState())
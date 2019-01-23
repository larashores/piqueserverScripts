import argparse
import enum


class Commands(enum.Enum):
    NONE = None

    SET = 'set'
    ADD = 'add'
    DEL = 'del'
    LIST = 'list'

    HEIGHT = 'height'
    RAISE = 'raise'
    LOWER = 'lower'
    ELEVATOR = 'elevator'
    OUTPUT = 'output'
    TELEPORT = 'teleport'
    CHAT = 'chat'
    DAMAGE = 'damage'


signature = ('trigger', [])


class ParseError(Exception):
    def __init__(self, prog):
        self.parsed = prog.split()[1:]


class NoExitParser(argparse.ArgumentParser):
    def error(self, *args, **kwargs):
        raise ParseError(self.prog)


S_ACTION_USAGE = 'Usage: /action <{commands}>'

ACTION_ADD_SET_ACTIONS = ('height', 'raise', 'lower', 'elevator', 'output', 'teleport', 'chat', 'damage')
ACTION_COMMAND_USAGES = {
    'add': 'Usage: /action add <{}>',
    'set': 'Usage: /action add <{}>',
    'del': 'Usage: /action del <#|all>'
}

ACTION_COMMANDS = ('add', 'set', 'list', 'del')
ACTION_ADD_SET_USAGES = {
    'height': 'Usage: /action {} height <height> [speed=0.15] [delay]',
    'raise': 'Usage: /action {} raise <amount> [speed=0.15] [delay]',
    'lower': 'Usage: /action {} lower <amount> [speed=0.15] [delay]',
    'elevator': 'Usage: /action {} elevator <height> [speed=0.25] [delay] [wait=3.0]',
    'output': 'Usage: /action {} output [delay]',
    'teleport': 'Usage: /action {} teleport <x y z|where>',
    'chat': 'Usage: /action {} chat <text>',
    'damage': 'Usage: /action {} damage <amount>',
}


def create_add_set_subparsers(parent):
    subparsers = parent.add_subparsers(dest='add_command')
    height_parser = subparsers.add_parser('height')
    height_parser.add_argument('height', nargs='?', type=int)
    height_parser.add_argument('speed',  nargs='?', type=float, default=0.25)
    height_parser.add_argument('delay', nargs='?', type=float, default=0.0)

    raise_parser = subparsers.add_parser('raise')
    raise_parser.add_argument('amount', nargs='?', type=int)
    raise_parser.add_argument('speed',  nargs='?', type=float, default=0.25)
    raise_parser.add_argument('delay', nargs='?', type=float, default=0.0)

    lower_parser = subparsers.add_parser('lower')
    lower_parser.add_argument('amount', nargs='?', type=int)
    lower_parser.add_argument('speed',  nargs='?', type=float, default=0.25)
    lower_parser.add_argument('delay', nargs='?', type=float, default=0.0)

    elevator_parser = subparsers.add_parser('elevator')
    elevator_parser.add_argument('height', nargs='?', type=int)
    elevator_parser.add_argument('speed',  nargs='?', type=float, default=0.25)
    elevator_parser.add_argument('delay', nargs='?', type=float, default=0.0)
    elevator_parser.add_argument('wait', nargs='?', type=float, default=0.0)

    subparsers.add_parser('output')

    teleport_parser = subparsers.add_parser('teleport')
    teleport_parser.add_argument('first',  nargs='?')
    teleport_parser.add_argument('y', nargs='?', type=int)
    teleport_parser.add_argument('z', nargs='?', type=int)

    chat_parser = subparsers.add_parser('chat')
    chat_parser.add_argument('text')

    damage_parser = subparsers.add_parser('damage')
    damage_parser.add_argument('amount', type=int)

def create_parser():
    platform_parser = NoExitParser()
    platform_subparsers = platform_parser.add_subparsers(dest='command')

    set_parser = platform_subparsers.add_parser('set')
    create_add_set_subparsers(set_parser)

    add_parser = platform_subparsers.add_parser('add')
    create_add_set_subparsers(add_parser)

    parser = platform_subparsers.add_parser('del')
    parser.add_argument('specifier', nargs='?')

    platform_subparsers.add_parser('list')

    return platform_parser


if __name__ == '__main__':
    parser = create_parser()

    try:
        args = parser.parse_args(['add', 'adf'])

        command = Commands(args.command)
        if command == Commands.ADD or command == Commands.SET:
            add_command = Commands(args.add_command)
            if add_command == Commands.HEIGHT:
                if args.height is None:
                    print('Usage: /action add height <height> [speed=0.15] [delay]')
            elif add_command == Commands.RAISE:
                if args.amount is None:
                    print('Usage: /action add raise <amount> [speed=0.15] [delay]')
            elif add_command == Commands.LOWER:
                if args.amount is None:
                    print('Usage: /action add lower <amount> [speed=0.15] [delay]')
            elif add_command == Commands.ELEVATOR:
                if args.height is None:
                    print('Usage: /action add elevator <height> [speed=0.25] [delay] [wait=3.0]')
            elif add_command == Commands.OUTPUT:
                print('Usage: /action add output [delay]')
            elif add_command == Commands.TELEPORT:
                if args.first == 'where':
                    print('doing teleport where')
                else:
                    try:
                        x = int(args.first)
                        if args.y is None or args.z is None:
                            raise ValueError()
                        print('teleporting ', x, args.y, args.z)
                    except (ValueError, TypeError):
                        print('Usage: /action add teleport <x y z|where>')
            elif add_command == Commands.CHAT:
                print('parse chat')
            elif add_command == Commands.DAMAGE:
                print('parse damage', args.amount)
            else:
                print('add usage')
        elif command == Commands.DEL:
            if args.specifier is None:
                print('del usage')
            elif args.specifier is 'all':
                print('del all')
            else:
                print('del', int(args.specifier))
        elif command == Commands.LIST:
            print('Parsed: list')
        else:
            print('usage message')

    except ParseError as e:
        if len(e.parsed) == 1:
            command = e.parsed[0]
            print(ACTION_COMMAND_USAGES[command].format(ACTION_ADD_SET_ACTIONS))
        elif len(e.parsed == 2):
            pass
        print('error:', e.parsed)

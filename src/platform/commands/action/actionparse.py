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


if __name__ == '__main__':

    platform_parser = argparse.ArgumentParser(description='Creates or edit platforms')
    platform_subparsers = platform_parser.add_subparsers(dest='command')

    set_parser = platform_subparsers.add_parser(Commands.SET.value)

    add_parser = platform_subparsers.add_parser(Commands.ADD.value)
    add_subparsers = add_parser.add_subparsers(dest='add_command')
    height_parser = add_subparsers.add_parser(Commands.HEIGHT.value)
    height_parser.add_argument('height', nargs='?', type=int)
    height_parser.add_argument('speed',  nargs='?', type=float, default=0.25)
    height_parser.add_argument('delay', nargs='?', type=float, default=0.0)

    raise_parser = add_subparsers.add_parser(Commands.RAISE.value)
    height_parser.add_argument('amount', nargs='?', type=int)
    height_parser.add_argument('speed',  nargs='?', type=float, default=0.25)
    height_parser.add_argument('delay', nargs='?', type=float, default=0.0)

    lower_parser = add_subparsers.add_parser(Commands.LOWER.value)
    height_parser.add_argument('amount', nargs='?', type=int)
    height_parser.add_argument('speed',  nargs='?', type=float, default=0.25)
    height_parser.add_argument('delay', nargs='?', type=float, default=0.0)

    elevator_parser = add_subparsers.add_parser(Commands.ELEVATOR.value)
    elevator_parser.add_argument('height', nargs='?', type=int)
    elevator_parser.add_argument('speed',  nargs='?', type=float, default=0.25)
    elevator_parser.add_argument('delay', nargs='?', type=float, default=0.0)
    elevator_parser.add_argument('wait', nargs='?', type=float, default=0.0)

    output_parser = add_subparsers.add_parser(Commands.OUTPUT.value)

    teleport_parser = add_subparsers.add_parser(Commands.TELEPORT.value)
    teleport_parser.add_argument('first',  nargs='?')
    teleport_parser.add_argument('y', nargs='?', type=int)
    teleport_parser.add_argument('z', nargs='?', type=int)

    chat_parser = add_subparsers.add_parser(Commands.CHAT.value)
    chat_parser.add_argument('text')

    damage_parser = add_subparsers.add_parser(Commands.DAMAGE.value)
    damage_parser.add_argument('amount', type=int)

    parser = platform_subparsers.add_parser(Commands.DEL.value)
    parser.add_argument('specifier', nargs='?')

    parser = platform_subparsers.add_parser(Commands.LIST.value)

    args = argparse.Namespace()
    platform_parser.parse_args(['add', 'teleport', '4', '3'], namespace=args)
    print(args)

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

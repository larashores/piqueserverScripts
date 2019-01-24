"""
/p /platforms [command]
    Starts a new platforms or enables you to edit them by specifying a command.
    To build a platforms, put down blocks delimiting the size of the floor--
    two blocks in opposite corners is sufficient.

    Press the SNEAK key (V) while in any platforms mode to get information
    about the platforms you're looking at.  Must be holding spade tool.

    command:
        new <label>
            Starts a new platforms with a label already attached.
        name <label>
            Labels a platforms.  It's recommended you name things to avoid mistakes.
        height <height>
            Forces the platforms to grow or shrink to the specified height.
        freeze
            Freezes or unfreezes a platforms.  A frozen platforms won't move.
        destroy
            Destroys a platforms, removing all its blocks.
        last
            When you get asked to select a platforms, you can use this command
            to automatically choose the last platforms you selected or created.
"""
import click

from platforms import piqueargs


@piqueargs.group(usage='Usage: /platform [new name height freeze destroy last]')
def platform_command(connection):
    pass


@piqueargs.argument('label')
@platform_command.command(usage='Usage: /platform new <label>')
def new(connection, label):
    return 'new {}'.format(label)


@piqueargs.argument('label')
@platform_command.command(usage='Usage: /platform name <label>')
def name(connection, label):
    return 'name {}'.format(label)


@piqueargs.argument('height', type=click.INT)
@platform_command.command(usage='Usage: /platform height <height>')
def height(connection, height):
    return 'name {}'.format(height)


@platform_command.command(usage='Usage: /platform freeze')
def freeze(connection):
    return 'freeze'


@platform_command.command(usage='Usage: /platform destroy')
def destroy(connection):
    return 'destroy'


@platform_command.command(usage='Usage: /platform last')
def last(connection):
    pass


if __name__ == '__main__':
    result = platform_command.run('connection', [])
    print(result)


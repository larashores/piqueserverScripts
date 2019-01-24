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
        destroy
            Destroys a button, removing the block.
        last
            When you get asked to select a button, you can use this command
            to automatically choose the last button you selected or created.
"""
import click

from platforms import piqueargs


@piqueargs.group(usage="Usage: /button [new name destroy toggle cooldown last]")
def button_command(connection):
    pass


@piqueargs.argument('label')
@button_command.command(usage='Usage: /button new <label>')
def new(connection, label):
    return 'new {}'.format(label)


@piqueargs.argument('label')
@button_command.command(usage='Usage: /button name <label>')
def name(connection, label):
    return 'name {}'.format(label)


@piqueargs.argument('seconds', type=click.INT)
@button_command.command(usage='Usage: /button cooldown <seconds>')
def cooldown(connection, seconds):
    return 'cooldown {}'.format(seconds)


@button_command.command(usage='Usage: /button destroy')
def destroy(connection):
    return 'destroy'


@button_command.command(usage='Usage: /button last')
def last(connection):
    return 'last'


if __name__ == '__main__':
    result = button_command.run('button_command', [])
    print(result)

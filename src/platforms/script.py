"""
Platforms!

Just knowing the names of the four commands should be enough in-game,
as the parameter lists are provided when you try them.

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
        quiet
            Makes a button either become silent or resume playing animation and
            sound when it activates.
        destroy
            Destroys a button, removing the block.
        last
            When you get asked to select a button, you can use this command
            to automatically choose the last button you selected or created.

/ac /action <command>
    Makes a button do something.

    command:
        add <action>
        set <action>
            Adds an action to the button. Set deletes all previous actions first,
            making the new action the only one.

            See /trigger for more information on who the "activating players" are.

            action:
                height   <height> [speed=0.15] [delay]
                raise    <amount> [speed=0.15] [delay]
                lower    <amount> [speed=0.15] [delay]
                elevator <height> [speed=0.25] [delay] [wait=3.0]
                    Speed determines how fast the platforms moves, in seconds.
                    Delay is the amount of time spent waiting before the platforms
                    actually starts to move.
                    Elevators can wait an amount of time at the end of the journey,
                    before heading back.
                teleport <x y _z|where>
                    Moves the activating players to the specified coordinates.
                    Using 'where' instead takes the last location where you stood
                    and executed the /where command.
                chat <text>
                    Sends text to the activating players.
                    You can put text between quotation marks to allow right
                    justifying with spaces, for example: "           Hello!"
                damage <amount>
                    Hits the activating players for that many hitpoints.
                    Use negative numbers to heal.
        list
            Lists the actions present in the button you select.

            Example:
            "Actions in 'mybutton': #0 platforms 'myplat' height(5) --
                #1 player teleport(16, 16, 32)"

            #0 and #1 are the action indexes to be used with /action del.
            'myplat' is the name of the platforms the height action is affecting,
            in this case making it 5 blocks tall.
        del <#|all>
            Delete a single action in a button by specifying its index. Action
            indexes can be looked up by using /action list.

            Negative indexes can be used too: -1 is the last added action, -2 the
            one before that, and so on.

            Specifying 'all' instead of a number erases all the actions.

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
                timer <time> [amount=-1]
                    Runs automatically ever 'time' seconds for 'amount' amount of
                    times or forever if -1
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

/save
    Saves all platforms and button data to mapname_platform.txt
    Use SAVE_ON_MAP_CHANGE and AUTOSAVE_EVERY to avoid having to manually save.

/reach
    Increases your button activation reach. Meant to be used for getting rid
    of distance triggering buttons from a safe distance.

    Use again to revert to normal.
"""

# TODO
# Platforms 'freeze' when people spam the button
# Shoot trigger or destroy trigger (both?)
# Grenade launching action
# Prevent platforms from being hidden forever
# Nicer way of having invisible buttons?
# Platforms crushing players
# Stop platforms action?

from piqueparser import piqueargs
from platforms.commands.buttoncommand import button
from platforms.commands.platformcommand import platform
from platforms.commands.triggercommand import trigger
from platforms.commands.actioncommand import action
from platforms.core.platformprotocol import platform_protocol
from platforms.core.platformconnection import platform_connection
from cbc.core import cbc


piqueargs.add_server_command(button, 'button', 'b')
piqueargs.add_server_command(platform, 'platform', 'p')
piqueargs.add_server_command(trigger, 'trigger', 'tr')
piqueargs.add_server_command(action, 'action', 'ac')


@piqueargs.command(usage=r'Usage: \save')
def save(connection):
    connection.protocol.dump_platform_json()
    return 'Platforms saved'


def apply_script(protocol, connection, config):
    protocol, connection = cbc.apply_script(protocol, connection, config)
    return platform_protocol(protocol), platform_connection(connection)

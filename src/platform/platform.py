"""
Platforms!

Just knowing the names of the four commands should be enough ingame,
as the parameter lists are provided when you try them.

/p /platform [command]
    Starts a new platform or enables you to edit them by specifying a command.
    To build a platform, put down blocks delimiting the size of the floor--
    two blocks in opposite corners is sufficient.

    Press the SNEAK key (V) while in any platform mode to get information
    about the platform you're looking at.  Must be holding spade tool.

    command:
        new <label>
            Starts a new platform with a label already attached.
        name <label>
            Labels a platform.  It's recommended you name things to avoid mistakes.
        height <height>
            Forces the platform to grow or shrink to the specified height.
        freeze
            Freezes or unfreezes a platform.  A frozen platform won't move.
        destroy
            Destroys a platform, removing all its blocks.
        last
            When you get asked to select a platform, you can use this command
            to automatically choose the last platform you selected or created.

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
                    Speed determines how fast the platform moves, in seconds.
                    Delay is the amount of time spent waiting before the platform
                    actually starts to move.
                    Elevators can wait an amount of time at the end of the journey,
                    before heading back.
                output
                teleport <x y z|where>
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
            "Actions in 'mybutton': #0 platform 'myplat' height(5) --
                #1 player teleport(16, 16, 32)"

            #0 and #1 are the action indexes to be used with /action del.
            'myplat' is the name of the platform the height action is affecting,
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
                track [radius=3]
                    Same as distance, but tracks one player and only one player.

                    Useful for creating a button that requires a specific number
                    of nearby players.
                height <height>
                    True when the platform is exactly the specified height.
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
        quiet
            Makes a button either become silent or resume playing animation and
            sound when it activates.

/save
    Saves all platform and button data to mapname_platform.txt
    Use SAVE_ON_MAP_CHANGE and AUTOSAVE_EVERY to avoid having to manually save.

/reach
    Increases your button activation reach. Meant to be used for getting rid
    of distance triggering buttons from a safe distance.

    Use again to revert to normal.

Maintainer: hompy
"""

# TODO
# Platforms 'freeze' when people spam the button
# Shoot trigger or destroy trigger (both?)
# Grenade launching action
# Prevent platforms from being hidden forever
# Negative heights
# Nicer way of having invisible buttons?
# Platforms crushing players
# Stop platform action?

import __builtin__
import json
import os
import operator
from collections import defaultdict
from itertools import product, imap, chain
from twisted.internet.reactor import callLater, seconds
from twisted.internet.task import LoopingCall
from pyspades.world import cube_line
from pyspades.server import block_action, block_line, set_color, position_data
from pyspades.collision import collision_3d
from pyspades.common import make_color
from pyspades.types import MultikeyDict
from pyspades.constants import *
from piqueserver.commands import add, admin, name, alias, join_arguments
from piqueserver import cfg

DEFAULT_LOAD_DIR = os.path.join(cfg.config_dir, 'maps')
SAVE_ON_MAP_CHANGE = True
AUTOSAVE_EVERY = 0.0 # minutes, 0 = disabled
MAX_DISTANCE = 64.0

S_SAVED = 'Platforms saved'
S_REACH = 'You can now reach to buttons from from far away'
S_NO_REACH = 'Button reach reverted to normal'
S_EXIT_BLOCKING_STATE = "You must first leave {state} mode!"
S_NOT_WORKING = 'This button is disabled'
S_COMMAND_CANCEL = "Aborting {command} command"
S_PLATFORM_NEW_USAGE = 'Usage: /platform new <label>'
S_PLATFORM_NAME_USAGE = 'Usage: /platform name <label>'
S_PLATFORM_HEIGHT_USAGE = 'Usage: /platform height <height>'
S_PLATFORM_STARTED = 'Platform construction started. Build then type ' \
    '/platform when done'
S_PLATFORM_NOT_FLAT = 'Bad platform. Floor can be incomplete but must be flat'
S_PLATFORM_CREATED = "Platform '{label}' created"
S_PLATFORM_CANCEL = 'Platform construction cancelled'
S_PLATFORM_RENAMED = "Platform '{old_label}' renamed to '{label}'"
S_PLATFORM_DESTROYED = "Platform '{label}' destroyed"
S_SELECT_PLATFORM = 'Select a platform by hitting it with the spade'
S_PLATFORM_SELECTED = "Platform '{label}' selected"
S_PLATFORM_INFO = "Platform '{label}', height {height}"
S_NOT_A_PLATFORM = 'This is not a platform!'
S_FROZEN = "Platform '{label}' frozen"
S_UNFROZEN = "Platform '{label}' unfrozen"
S_BUTTON_NEW_USAGE = 'Usage: /button new <label>'
S_BUTTON_NAME_USAGE = 'Usage: /button name <label>'
S_BUTTON_COOLDOWN_USAGE = 'Usage: /button cooldown <seconds>'
S_BUTTON_PLACEMENT = 'Put down a block where you want the new button to be'
S_BUTTON_CREATED = "Button '{label}' created"
S_BUTTON_CANCEL = 'Aborting button placement'
S_BUTTON_OVERLAPS = 'There is already another button here!'
S_BUTTON_RENAMED = "Button '{old_label}' renamed to '{label}'"
S_BUTTON_DESTROYED = "Button '{label}' removed"
S_BUTTON_COOLDOWN = "Cooldown for button '{label}' set to {cooldown:.2f} seconds"
S_SELECT_BUTTON = 'Select a button by hitting it with the spade'
S_BUTTON_SELECTED = "Button '{label}' selected"
S_BUTTON_INFO = "Button '{label}', cooldown {cooldown:.2f}s"
S_DISABLED = "Button '{label}' disabled"
S_ENABLED = "Button '{label}' enabled"
S_SILENT = "Button '{label}' will activate quietly"
S_NOISY = "Button '{label}' will animate when activated"
S_ACTION_ADD_USAGE = 'Usage: /action add <{actions}>'
S_ACTION_DELETE_USAGE = 'Usage: /action del <#|all>'
S_ACTION_HEIGHT_USAGE = 'Usage: /action add height <height> [speed=0.15] [delay]'
S_ACTION_RAISE_USAGE = 'Usage: /action add raise <amount> [speed=0.15] [delay]'
S_ACTION_LOWER_USAGE = 'Usage: /action add lower <amount> [speed=0.15] [delay]'
S_ACTION_ELEVATOR_USAGE = 'Usage: /action add elevator <height> [speed=0.25] ' \
    '[delay] [wait=3.0]'
S_ACTION_OUTPUT_USAGE = 'Usage: /action add output [delay]'
S_ACTION_TELEPORT_USAGE = 'Usage: /action add teleport <x y z|where>'
S_ACTION_CHAT_USAGE = 'Usage: /action add chat <text>'
S_ACTION_DAMAGE_USAGE = 'Usage: /action add damage <amount>'
S_ACTION_ADDED = "Added {action} action to button '{label}'"
S_ACTION_LIST_EMPTY = "Button '{label}' has no actions"
S_ACTION_LIST_HEADER = "Actions in '{label}': "
S_ACTION_DELETED = "{action} action {number} deleted from button '{label}'"
S_ACTION_DELETED_ALL = "Deleted all actions in button '{label}'"
S_ACTION_INVALID_NUMBER = "Invalid action number! Use '/action list' to check"
S_TRIGGER_ADD_USAGE = 'Usage: /trigger add [not] <{triggers}>'
S_TRIGGER_DELETE_USAGE = 'Usage: /trigger del <#|all>'
S_TRIGGER_LOGIC_USAGE = 'Usage: /trigger logic <and|or>'
S_TRIGGER_DISTANCE_USAGE = 'Usage: /trigger add [not] distance [radius=3]'
S_TRIGGER_TRACK_USAGE = 'Usage: /trigger add [not] track [radius=3]'
S_TRIGGER_HEIGHT_USAGE = 'Usage: /trigger add [not] height <height>'
S_TRIGGER_ADDED = "Added {trigger} trigger to button '{label}'"
S_TRIGGER_LIST_EMPTY = "Button '{label}' has no triggers"
S_TRIGGER_LIST_HEADER = "Triggers in '{label}': "
S_TRIGGER_LIST_ITEM_IS_TRUE = ' [CHECK]'
S_TRIGGER_LIST_AND = ' AND '
S_TRIGGER_LIST_OR = ' OR '
S_TRIGGER_LIST_NOT = 'NOT '
S_TRIGGER_DELETED = "{trigger} trigger {number} deleted from button '{label}'"
S_TRIGGER_DELETED_ALL = "Deleted all triggers in button '{label}'"
S_TRIGGER_INVALID_NUMBER = "Invalid trigger number! Use '/trigger list' to check"
S_LOGIC_AND = "Button '{label}' will activate when ALL its triggers yield true"
S_LOGIC_OR = "Button '{label}' will activate when ANY of its triggers fire"
S_NOT_POSITIVE = 'ERROR: {parameter} must be a positive number'
S_OUT_OF_BOUNDS = 'ERROR: {parameter} must be in the range [0..512)'
S_OUT_OF_BOUNDS_Z = 'ERROR: {parameter} must be in the range [0..62]'
S_WHERE_FIRST = 'ERROR: use /where first to remember your position'
S_MINIMUM = 'ERROR: Minimum {parameter} is {value}'
S_MAXIMUM = 'ERROR: Maximum {parameter} is {value}'
S_NICE_LOCATION = '{:.4g}, {:.4g}, {:.4g}'
PLATFORM_COMMANDS = ('new', 'name', 'height', 'freeze', 'destroy',  'last')
PLATFORM_COMMAND_USAGES = {
    'new' : S_PLATFORM_NEW_USAGE,
    'name' : S_PLATFORM_NAME_USAGE,
    'height' : S_PLATFORM_HEIGHT_USAGE
}
BUTTON_COMMAND_USAGES = {
    'new' : S_BUTTON_NEW_USAGE,
    'name' : S_BUTTON_NAME_USAGE,
    'cooldown' : S_BUTTON_COOLDOWN_USAGE
}
ACTION_COMMANDS = ('add', 'set', 'list', 'del')
ACTION_COMMAND_USAGES = {
    'add' : S_ACTION_ADD_USAGE,
    'del' : S_ACTION_DELETE_USAGE
}
ACTION_ADD_ACTIONS = ('height', 'raise', 'lower', 'elevator', 'output',
    'teleport', 'chat', 'damage')
ACTION_ADD_USAGES = {
    'height' : S_ACTION_HEIGHT_USAGE,
    'raise' : S_ACTION_RAISE_USAGE,
    'lower' : S_ACTION_LOWER_USAGE,
    'elevator' : S_ACTION_ELEVATOR_USAGE,
    'output' : S_ACTION_OUTPUT_USAGE,
    'teleport' : S_ACTION_TELEPORT_USAGE,
    'chat' : S_ACTION_CHAT_USAGE,
    'damage' : S_ACTION_DAMAGE_USAGE,
}
TRIGGER_COMMANDS = ('add', 'set', 'list', 'del', 'logic', 'quiet')
TRIGGER_COMMAND_USAGES = {
    'add' : S_TRIGGER_ADD_USAGE,
    'del' : S_TRIGGER_DELETE_USAGE,
    'logic' : S_TRIGGER_LOGIC_USAGE
}
TRIGGER_ADD_TRIGGERS = ('press', 'distance', 'track', 'height')
TRIGGER_ADD_USAGES = {
    'distance' : S_TRIGGER_DISTANCE_USAGE,
    'track' : S_TRIGGER_TRACK_USAGE,
    'height' : S_TRIGGER_HEIGHT_USAGE,
}

ACTION_RAY_LENGTH = 8.0
ACTION_RAY_LENGTH_LONG = 32.0
ACTION_COOLDOWN = 0.25


def flatten(iterables):
    return chain.from_iterable(iterables)

@admin
def save(connection):
    connection.protocol.dump_platform_json()
    return S_SAVED

@admin
def reach(connection):
    if connection not in connection.protocol.players:
        raise ValueError()
    long = connection.reach == ACTION_RAY_LENGTH_LONG
    connection.reach = ACTION_RAY_LENGTH if long else ACTION_RAY_LENGTH_LONG
    return S_REACH if not long else S_NO_REACH


def aabb(x, y, z, x1, y1, z1, x2, y2, z2):
    return x >= x1 and y >= y1 and z >= z1 and x < x2 and y < y2 and z < z2

def prism(x1, y1, z1, x2, y2, z2):
    return product(range(x1, x2), range(y1, y2), range(z1, z2))

def plane_least_rows(x1, y1, x2, y2, z):
    if y2 - y1 < x2 - x1:
        for y in range(y1, y2):
            yield x1, y, z, x2 - 1, y, z
    else:
        for x in range(x1, x2):
            yield x, y1, z, x, y2 - 1, z

def send_color(protocol, color):
    set_color.value = make_color(*color)
    set_color.player_id = 32
    protocol.send_contained(set_color, save = True)

def send_block(protocol, x, y, z, value = BUILD_BLOCK):
    block_action.value = value
    block_action.player_id = 32
    block_action.x = x
    block_action.y = y
    block_action.z = z
    protocol.send_contained(block_action, save = True)




TRIGGER_CLASSES = {}
for cls in (PressTrigger, TrackTrigger, DistanceTrigger, HeightTrigger):
    TRIGGER_CLASSES[cls.type] = cls





ACTION_CLASSES = {}
for cls in (PlatformAction, PlayerAction):
    ACTION_CLASSES[cls.type] = cls


def apply_script(protocol, connection, config):


    return PlatformProtocol, PlatformConnection
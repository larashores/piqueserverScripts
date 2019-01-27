from pyspades.constants import DESTROY_BLOCK, BUILD_BLOCK
from platforms.worldobjects.baseobject import BaseObject
from platforms.util.packets import send_block, send_color

from collections import defaultdict
from itertools import chain
import itertools
from twisted.internet.reactor import callLater, LoopingCall
import enum


class LogicType(enum.Enum):
    AND = 0
    OR = 1


class Button(BaseObject):

    def __init__(self, protocol, id_, x, y, z, color):
        BaseObject.__init__(self, protocol, id_)
        self.label = str(self.id)
        self.x, self.y, self.z = x, y, z
        self.logic = LogicType.AND
        self.disabled = False
        self.silent = False
        self.cooldown = 0.5
        self._actions = []
        self._triggers = []
        self._action_pending = False
        self._color = color
        self._color_triggered = tuple(int(c * 0.2) for c in color)
        self._cooldown_call = None
        protocol.map.set_point(x, y, z, self._color)

    def release(self):
        """Removes the button from the world, but leaves the block as is"""
        self.clear_triggers()
        if self._cooldown_call and self._cooldown_call.active():
            self._cooldown_call.cancel()
            self._cooldown_call = None
        for player in self.protocol.players.values():  # clear last button memory from players
            if player.last_button is self:
                player.last_button = None

    def destroy(self):
        """Removes the block from the world and destroys the map"""
        self.release()
        if self.protocol.map.destroy_point(self.x, self.y, self.z):
            send_block(self.protocol, self.x, self.y, self.z, DESTROY_BLOCK)

    def add_trigger(self, new_trigger):
        """
        Adds a new trigger to the button

        Connects to the trigger's signal_fire so that if any trigger checks, all triggers will be checked to see if the
        trigger condition has been met, and activate the button accordingly.
        """
        new_trigger.parent = self
        if new_trigger.ONE_PER_BUTTON:  # ensure there is only one trigger of this type
            to_remove = [t for t in self._triggers if isinstance(t, type(new_trigger))]
            for trigger in to_remove:
                self._remove_trigger(trigger)
        self._triggers.append(new_trigger)
        new_trigger.signal_fire.connect(self._trigger_check)

    def pop_trigger(self, index):
        """Removes a trigger by index"""
        trigger = self._triggers[index]
        self._remove_trigger(trigger)
        return trigger

    def clear_triggers(self):
        """Removes all triggers from the button"""
        for trigger in self._triggers:
            trigger.unbind()
        self._triggers.clear()

    def _remove_trigger(self, trigger):
        """Removes a trigger and stops it from activating the trigger check"""
        trigger.unbind()
        trigger.signal_fire.disconnect(self._trigger_check)
        self._triggers.remove(trigger)

    def _trigger_check(self):
        """
        Checks to see if any or all trigger conditions have been met and activates the button if so.

        If this trigger happened before the button cools down, wait until it cools down to check again
        """
        self._action_pending = False
        check = all if self.logic == LogicType.AND else any
        if check(trigger.get_status() for trigger in self._triggers):
            if self._cooldown_call:
                self._action_pending = True
            else:
                self._activate_button()

    def _activate_button(self):
        """
        Puts a button in its activated state if it is not disabled.

        Runs all actions if it is not disabled. If the button is disabled, notifies all affected players. If it is not
        silent, changes the color.
        """
        affected_players = set(chain.from_iterable(trigger.affected_players() for trigger in self._triggers))
        if self.disabled:
            if not self.silent:
                for player in affected_players:
                    player.send_chat('This button is disabled')
            return
        self._cooldown_call = callLater(self.cooldown, self._deactivate_button)
        for action in self._actions:
            action.run(True, affected_players)
        if not self.silent:
            self._build_block(self._color_triggered)

    def _deactivate_button(self):
        """
        Puts a button back in its deactivated state.

        Changes the color to normal if not silent. If an action was triggered before the cooldown is up, checks to see
        if the action should still be run
        """
        self._cooldown_call = None
        if not self.silent:
            self._build_block(self._color)
        if self._action_pending:
            self._trigger_check()

    def _build_block(self, color):
        """
        Immediately destroys a block and builds a block in its place with its color.

        Used to change a blocks color with an audible sound
        """
        send_block(self.protocol, self.x, self.y, self.z, DESTROY_BLOCK)
        send_color(self.protocol, color)
        send_block(self.protocol, self.x, self.y, self.z, BUILD_BLOCK)

    def serialize(self):
        return {
            'id': self.id,
            'location': (self.x, self.y, self.z),
            'label': self.label,
            'color': self._color,
            'actions': [action.serialize() for action in self._actions],
            'triggers': [trigger.serialize() for trigger in self._triggers],
            'logic': self.logic,
            'cooldown': self.cooldown,
            'disabled': self.disabled,
            'silent': self.silent
        }

from pyspades.constants import DESTROY_BLOCK, BUILD_BLOCK
from platforms.worldobjects.baseobject import BaseObject
from platforms.worldobjects.trigger.presstrigger import PressTrigger
from platforms.util.packets import send_block, send_color

from itertools import chain
from twisted.internet.reactor import callLater
import enum


class LogicType(enum.Enum):
    AND = 0
    OR = 1


class Button(BaseObject):
    location = property(lambda self: self._location)

    def __init__(self, protocol, id_, location, color, label=None):
        BaseObject.__init__(self, protocol, id_)
        self.label = label or str(self._id)
        self.disabled = False
        self.silent = False
        self.logic = LogicType.AND
        self.cooldown = 0.5
        self._location = location
        self._triggers = []
        self._actions = []
        self._triggers = []
        self._action_pending = False
        self._color = color
        self._color_triggered = tuple(int(c * 0.2) for c in color)
        self._cooldown_call = None

    def __str__(self):
        return "[{}] Button '{}' cooldown {:.2f}s logic '{}'".format('OFF' if self.disabled else 'ON',
                                                                   self.label, self.cooldown, self.logic.name)

    def destroy(self):
        if self._protocol.map.destroy_point(*self._location):
            send_block(self, *self._location, DESTROY_BLOCK)
        self.clear_triggers()
        if self._cooldown_call and self._cooldown_call.active():
            self._cooldown_call.cancel()
            self._cooldown_call = None

    def add_trigger(self, new_trigger):
        if new_trigger.ONE_PER_BUTTON:  # ensure there is only one trigger of this type
            to_remove = [t for t in self._triggers if isinstance(t, type(new_trigger))]
            for trigger in to_remove:
                self._remove_trigger(trigger)
        self._triggers.append(new_trigger)
        new_trigger.signal_fire.connect(self._trigger_check)

    def add_action(self, action):
        self._actions.append(action)

    def clear_triggers(self):
        for trigger in self._triggers:
            trigger.unbind()
        self._triggers.clear()

    def clear_actions(self):
        self._actions.clear()

    def press(self, player):
        for trigger in self._triggers:
            if isinstance(trigger, PressTrigger):
                trigger.update(player)

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
        affected_players = set(chain.from_iterable(trigger.affected_players for trigger in self._triggers))
        if self.disabled:
            if not self.silent:
                for player in affected_players:
                    player.send_chat('This button is disabled')
            return
        self._cooldown_call = callLater(self.cooldown, self._deactivate_button)
        for action in self._actions:
            action.run(affected_players)
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
        send_block(self._protocol, *self._location, DESTROY_BLOCK)
        send_color(self._protocol, color)
        send_block(self._protocol, *self._location, BUILD_BLOCK)

    # def pop_trigger(self, index):
    #     """Removes a trigger by index"""
    #     trigger = self._triggers[index]
    #     self._remove_trigger(trigger)
    #     return trigger
    #
    #
    # def serialize(self):
    #     return {
    #         'id': self._id,
    #         'location': self._location,
    #         'label': self.label,
    #         'color': self._color,
    #         'actions': [action.serialize() for action in self._actions],
    #         'triggers': [trigger.serialize() for trigger in self._triggers],
    #         'logic': self.logic,
    #         'cooldown': self.cooldown,
    #         'disabled': self.disabled,
    #         'silent': self.silent
    #     }

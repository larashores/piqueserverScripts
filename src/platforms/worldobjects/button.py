from pyspades.constants import DESTROY_BLOCK, BUILD_BLOCK
from platforms.worldobjects.baseobject import BaseObject
from platforms.worldobjects.trigger.presstrigger import PressTrigger, PlayerTrigger
from platforms.worldobjects.trigger.trigger import Trigger
from platforms.worldobjects.action.action import Action
from platforms.util.packets import send_block, send_color
from platforms.states.needsbuttonstate import NeedsButtonState


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
        self._action_pending = False
        self._color = color
        self._color_triggered = tuple(int(c * 0.2) for c in color)
        self._cooldown_call = None
        protocol.map.set_point(*location, self._color)

    def __str__(self):
        return "[{}] Button '{}' cooldown {:.2f}s logic '{}'".format('OFF' if self.disabled else 'ON',
                                                                     self.label, self.cooldown, self.logic.name)

    def destroy(self):
        if self._protocol.map.destroy_point(*self._location):
            send_block(self._protocol, *self._location, DESTROY_BLOCK)
        self.clear_triggers()
        if self._cooldown_call and self._cooldown_call.active():
            self._cooldown_call.cancel()
            self._cooldown_call = None

    def get_trigger_info(self):
        if not self._triggers:
            return "Button '{}' has no triggers".format(self.label)
        separator = ' {} '.format(self.logic.name)
        items = separator.join('#{}({}{})'.format(i, '[ON]' if trigger.status() else '', trigger)
                               for i, trigger in enumerate(self._triggers))
        return "Triggers in '{}': {}".format(self.label, items)

    def get_action_info(self):
        if not self._actions:
            return "Button '{}' has no actions".format(self.label)
        items = ', '.join('#{}({})'.format(i, action) for i, action in enumerate(self._actions))
        return "Actions in '{}': {}".format(self.label, items)

    def add_trigger(self, new_trigger):
        if new_trigger.ONE_PER_BUTTON:  # ensure there is only one trigger of this type
            to_remove = [t for t in self._triggers if isinstance(t, type(new_trigger))]
            for trigger in to_remove:
                trigger.destroy()
        self._triggers.append(new_trigger)
        new_trigger.signal_fire.connect(self.trigger_check)
        new_trigger.signal_remove.connect(self._triggers.remove)

    def add_action(self, action):
        self._actions.append(action)
        action.signal_remove.connect(self._actions.remove)

    def pop_trigger(self, index):
        trigger = self._triggers[index]
        trigger.destroy()
        return trigger

    def pop_action(self, index):
        action = self._actions.pop(index)
        action.destroy()
        return action

    def clear_triggers(self):
        for trigger in self._triggers.copy():
            trigger.destroy()

    def clear_actions(self):
        for action in self._actions.copy():
            action.destroy()

    def press(self, player):
        for trigger in self._triggers:
            if isinstance(trigger, PressTrigger):
                trigger.update(player)

    def trigger_check(self):
        """
        Checks to see if any or all trigger conditions have been met and activates the button if so.

        If this trigger happened before the button cools down, wait until it cools down to check again
        """
        self._action_pending = False
        check = all if self.logic == LogicType.AND else any
        if check(trigger.status() for trigger in self._triggers):
            if self._cooldown_call:
                self._action_pending = True
            else:
                self._activate_button()

    def serialize(self):
        return {
            'id': self._id,
            'location': self._location,
            'label': self.label,
            'color': self._color,
            'actions': [action.serialize() for action in self._actions],
            'triggers': [trigger.serialize() for trigger in self._triggers],
            'logic': self.logic.name.lower(),
            'cooldown': self.cooldown,
            'disabled': self.disabled,
            'silent': self.silent
        }

    @staticmethod
    def unserialize(protocol, data):
        id_ = data['id']
        location = tuple(data['location'])
        color = tuple(data['color'])
        label = data['label']
        button = Button(protocol, id_, location, color, label)
        button.logic = LogicType[data['logic'].upper()]
        button.cooldown = data['cooldown']
        button.disabled = data['disabled']
        button.silent = data['silent']
        for action_data in data['actions']:
            button.add_action(Action.unserialize(protocol, action_data))
        for trigger_data in data['triggers']:
            button.add_trigger(Trigger.unserialize(protocol, button, trigger_data))
        return button

    def _activate_button(self):
        """
        Puts a button in its activated state if it is not disabled.

        Runs all actions if it is not disabled. If the button is disabled, notifies all affected players. If it is not
        silent, changes the color.
        """
        affected_players = set()
        for trigger in self._triggers:  # Don't activate if editing buttons
            if isinstance(trigger, PlayerTrigger):
                for player in trigger.affected_players:
                    if not isinstance(player.state_stack.top(), NeedsButtonState):
                        affected_players.add(player)
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
            self.trigger_check()

    def _build_block(self, color):
        """
        Immediately destroys a block and builds a block in its place with its color.

        Used to change a blocks color with an audible sound
        """
        send_block(self._protocol, *self._location, DESTROY_BLOCK)
        send_color(self._protocol, color)
        send_block(self._protocol, *self._location, BUILD_BLOCK)

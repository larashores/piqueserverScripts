from pyspades.constants import DESTROY_BLOCK, BUILD_BLOCK
from platforms.wordobjects.baseobject import BaseObject
from platforms.util.packets import send_block, send_color

from collections import defaultdict
from itertools import chain
from twisted.internet.reactor import callLater

S_NOT_WORKING = 'This button is disabled'


def flatten(iterables):
    return chain.from_iterable(iterables)


class Button(BaseObject):
    label = None
    action_pending = False
    disabled = False
    silent = False
    cooldown_call = None

    def __init__(self, protocol, id, x, y, z, color):
        BaseObject.__init__(self, protocol, id)
        self.label = str(self.id)
        self.x, self.y, self.z = x, y, z
        self.color = color
        self.color_triggered = tuple(int(c * 0.2) for c in color)
        self.actions = []
        self.triggers = []
        self.shared_trigger_objects = defaultdict(set)
        self.logic = 'and'
        self.cooldown = 0.5
        protocol.map.set_point(x, y, z, self.color)

    def release(self):
        BaseObject.release(self)
        self.clear_triggers()
        if self.cooldown_call and self.cooldown_call.active():
            self.cooldown_call.cancel()
        self.cooldown_call = None

    def destroy(self):
        self.release()
        if self.protocol.map.destroy_point(self.x, self.y, self.z):
            send_block(self.protocol, self.x, self.y, self.z, DESTROY_BLOCK)

    def add_trigger(self, new_trigger):
        new_trigger.parent = self
        if new_trigger.unique:
            # ensure there is only one trigger of this type
            remove_triggers = [trigger for trigger in self.triggers if
                trigger.type == new_trigger.type]
            for trigger in remove_triggers:
                trigger.unbind()
        self.triggers.append(new_trigger)
        self.trigger_check()

    def clear_triggers(self):
        for trigger in self.triggers[:]:
            trigger.unbind()

    def trigger_check(self):
        self.action_pending = False
        check = all if self.logic == 'and' else any
        if check(trigger.get_status() for trigger in self.triggers):
            if self.cooldown_call:
                # schedule action for after the button resets
                self.action_pending = True
            else:
                self.action()
        else:
            for action in self.actions:
                action.run(False, None)

    def action(self):
        self.cooldown_call = callLater(self.cooldown, self.reset)
        objects = set(flatten(self.shared_trigger_objects.itervalues()))
        if self.disabled:
            if not self.silent:
                for player in objects:
                    player.send_chat(S_NOT_WORKING)
            return
        for action in self.actions:
            action.run(True, objects)
        if not self.silent:
            self.build_block(self.color_triggered)

    def reset(self):
        self.cooldown_call = None
        if not self.silent and not self.disabled:
            self.build_block(self.color)
        if self.action_pending:
            # ensure conditions are still met
            self.trigger_check()

    def build_block(self, color):
        send_block(self.protocol, self.x, self.y, self.z, DESTROY_BLOCK)
        send_color(self.protocol, color)
        send_block(self.protocol, self.x, self.y, self.z, BUILD_BLOCK)

    def serialize(self):
        return {
            'id': self.id,
            'location': (self.x, self.y, self.z),
            'label': self.label,
            'color': self.color,
            'actions': [action.serialize() for action in self.actions],
            'triggers': [trigger.serialize() for trigger in self.triggers],
            'logic': self.logic,
            'cooldown': self.cooldown,
            'disabled': self.disabled,
            'silent': self.silent
        }

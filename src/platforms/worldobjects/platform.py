from platforms.worldobjects.baseobject import BaseObject
from platforms.util.geometry import aabb_collision
from platforms.util.packets import send_position

from twisted.internet.reactor import callLater, seconds
from twisted.internet.task import LoopingCall
from cbc.core.buildbox import build_filled
from cbc.core.clearbox import clear_solid


class Platform(BaseObject):
    height = property(lambda self: self._start_z - self._z)

    def __init__(self, protocol, id_, location1, location2, z, color, label=None):
        BaseObject.__init__(self, protocol, id_)
        self.label = label or str(self._id)
        self._frozen = False
        self._protocol = protocol
        self._color = color
        self._triggers = set()
        self._actions = set()
        self._location1 = location1
        self._location2 = location2
        self._start_z = z
        self._z = self._target_z = self._start_z - 1
        self._build_plane(self._z)
        self._cycle_loop = LoopingCall(self._cycle)
        self._cycle_loop_deferred = None
        self._cycle_start_call = None
        self._cycle_start_remaining = None
        self._original_z = None
        self._cycle_loop_paused = False
        self._speed = 0.0
        self._wait = 0.0

    def destroy(self):
        if self._cycle_start_call is not None and self._cycle_start_call.active():
            self._cycle_start_call.cancel()
        if self._cycle_loop.running:
            self._cycle_loop.stop()
        for trigger in self._triggers.copy():
            trigger.destroy()
        for action in self._actions.copy():
            action.destroy()
        clear_solid(self._protocol, *self._location1, self._z, *self._location2, self._start_z)

    @property
    def frozen(self):
        return self._frozen

    @frozen.setter
    def frozen(self, value):
        self._frozen = value
        if self._frozen:
            self._pause_cycle()
        else:
            self._unpause_cycle()

    def add_trigger(self, trigger):
        self._triggers.add(trigger)
        trigger.signal_remove.connect(self._triggers.remove)

    def add_action(self, action):
        self._actions.add(action)
        action.signal_remove.connect(self._actions.remove)

    def contains(self, location):
        if self._z < self._start_z:
            z1 = self._z + 1
            z2 = self._start_z
        elif self._z > self._start_z:
            z1 = self._start_z + 1
            z2 = self._z
        else:
            return False
        return aabb_collision(*location, *self._location1, z1, *self._location2, z2)

    def raise_(self, amount, speed=0.0, delay=0.0):
        self.set_height(self.height + amount, speed, delay)

    def lower(self, amount, speed=0.0, delay=0.0):
        self.set_height(self.height - amount, speed, delay)

    def set_height(self, height, speed=0.0, delay=0.0, go_back_at_end=False, wait=0.0):
        if self._cycle_start_call is not None:
            return
        self._speed = speed
        self._wait = wait
        self._original_z = self._z if go_back_at_end else None
        self._target_z = min(max(0, self._start_z - height), 62)
        self._cycle_later(delay)

    def serialize(self):
        return {
            'id': self._id,
            'start': (*self._location1, self._start_z),
            'end': (*self._location2, self._target_z),
            'label': self.label,
            'color': self._color,
            'frozen': self.frozen
        }

    def _cycle_later(self, delay):
        self._cycle_start_call = callLater(delay, self._start_cycle)

    def _start_cycle(self):
        self._cycle_loop_deferred = self._cycle_loop.start(self._speed)

    def _stop_cycle(self):
        self._cycle_loop.stop()
        self._cycle_loop_deferred = None

    def _pause_cycle(self):
        if self._cycle_start_call is not None and self._cycle_start_call.active():
            time = self._cycle_start_call.getTime()
            self._cycle_start_call.cancel()
            self._cycle_start_remaining = time - seconds()
        elif self._cycle_loop_deferred is not None:
            self._cycle_loop_deferred.pause()

    def _unpause_cycle(self):
        if self._cycle_start_remaining is not None:
            self._cycle_later(self._cycle_start_remaining)
        elif self._cycle_loop_deferred is not None:
            self._cycle_loop_deferred.unpause()

    def _cycle(self):
        if self.frozen:
            return
        if self._target_z > self._z:          # Going down
            if self._z < self._start_z:       # Above zero
                self._destroy_plane(self._z)
            else:                             # Below or at zero
                self._build_plane(self._z)
            self._z += 1
        elif self._target_z < self._z:        # Going up
            self._z -= 1
            if self._z < self._start_z:       # Above or at zero
                self._build_plane(self._z)
                self._unstick()
            else:                             # Below zero
                self._destroy_plane(self._z)
        if self._z == self._target_z:
            self._stop_cycle()
            if self._original_z is not None:
                self._target_z, self._original_z = self._original_z, None
                self._cycle_later(self._wait)
            else:
                self._cycle_start_call = None
        self._update_triggers()

    def _build_plane(self, z):
        build_filled(self._protocol, *self._location1, z + 1, *self._location2, z + 1, self._color)

    def _destroy_plane(self, z):
        clear_solid(self._protocol, *self._location1, z + 1, *self._location2, z + 1)

    def _unstick(self):
        for player in self._protocol.players.values():
            obj = player.world_object
            if obj is None:
                continue
            location = list(obj.position.get())
            if aabb_collision(*location, *self._location1, self._z - 2, *self._location2, self._start_z):
                location[2] -= 1.4 if not obj.crouch else -2.4
                send_position(player, *location)
                obj.position.z = location[2]

    def _update_triggers(self):
        for trigger in self._triggers:
            trigger.update()

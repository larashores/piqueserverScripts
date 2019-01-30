from platforms.worldobjects.baseobject import BaseObject
from platforms.util.geometry import aabb_collision
from platforms.util.packets import send_position

from twisted.internet.reactor import callLater
from twisted.internet.task import LoopingCall
from cbc.core.buildbox import build_filled
from cbc.core.clearbox import clear_solid


class Platform(BaseObject):
    height = property(lambda self: self._start_z - self._z + 1)

    def __init__(self, protocol, id_, location1, location2, z, color, label=None):
        BaseObject.__init__(self, protocol, id_)
        self.label = label or str(self._id)
        self.frozen = False
        self._protocol = protocol
        self._color = color
        self._triggers = set()
        self._location1 = location1
        self._location2 = location2
        self._start_z = self._z = self._target_z = z
        self._build_plane(self._start_z)
        self._cycle_loop = LoopingCall(self._cycle)
        self._cycle_start_call = None
        self._original_height = None
        self._speed = 0.0
        self._wait = 0.0

    def add_trigger(self, trigger):
        self._triggers.add(trigger)

    def remove_trigger(self, trigger):
        self._triggers.remove(trigger)

    def contains(self, location):
        return aabb_collision(*location, *self._location1, self._z, *self._location2, self._start_z)

    def raise_(self, amount, speed=0.0, delay=0.0):
        self.height(self._z - amount, speed, delay)

    def lower(self, amount, speed=0.0, delay=0.0):
        self.height(self._z + amount, speed, delay)

    def set_height(self, height, speed=0.0, delay=0.0, go_back_at_end=False, wait=0.0):
        if self._cycle_start_call is not None:
            return
        self._speed = speed
        self._wait = wait
        self._original_height = self._z if go_back_at_end else None
        self._target_z = self._start_z - height + 1
        self._cycle_later(delay)

    def destroy(self):
        clear_solid(self._protocol, *self._location1, self._z, *self._location2, self._start_z)

    def _cycle_later(self, delay):
        self._cycle_start_call = callLater(delay, self._cycle_loop.start, self._speed)

    def _cycle(self):
        if self.frozen:
            return
        if self._z > self._target_z:
            self._z -= 1
            self._build_plane(self._z)
            self._unstick()
        elif self._z < self._target_z:
            self._destroy_plane(self._z)
            self._z += 1
        if self._z == self._target_z:
            self._cycle_loop.stop()
            if self._original_height is not None:
                self._target_z, self._original_height = self._original_height, None
                self._cycle_later(self._wait)
            else:
                self._cycle_start_call = None
        self._update_triggers()

    def _build_plane(self, z):
        build_filled(self._protocol, *self._location1, z, *self._location2, z, self._color)

    def _destroy_plane(self, z):
        clear_solid(self._protocol, *self._location1, z, *self._location2, z)

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

    #     self.label = str(self.id)
    #     self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
    #     self.z, self.start_z = z1, z2
    #     self.height = self.start_z - self.z
    #     self.color = color
    #     for x, y, z in prism(x1, y1, z1, x2, y2, z2):
    #         protocol.map.set_point(x, y, z, color)
    #
    # def overlaps(self, p):
    #     return (self.x1 <= p.x2 and self.y1 <= p.y2 and self.z <= p.start_z and
    #             self.x2 >= p.x1 and self.y2 >= p.y1 and self.start_z >= p.z)
    #
    #
    # def release(self):
    #     BaseObject.release(self)
    #     if self.bound_triggers:
    #         bound_buttons = set()
    #         for trigger in self.bound_triggers[:]:
    #             bound_buttons.add(trigger.parent)
    #             trigger.unbind()
    #         for button in bound_buttons:
    #             button.trigger_check()
    #     if self.delay_call and self.delay_call.active():
    #         self.delay_call.cancel()
    #     self.delay_call = None
    #
    # def run(self):
    #     self.running = True
    #     self.protocol.running_platforms.add(self)
    #
    # def serialize(self):
    #     z = self.last_z if self.mode == 'elevator' else self.target_z
    #     return {
    #         'id' : self.id,
    #         'start' : (self.x1, self.y1, z or self.z),
    #         'end' : (self.x2, self.y2, self.start_z),
    #         'label' : self.label,
    #         'color' : self.color,
    #         'frozen' : self.frozen
    #     }

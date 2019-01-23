from pyspades.constants import DESTROY_BLOCK, UPDATE_FREQUENCY
from pyspades.contained import BlockLine, PositionData
from pyspades.world import cube_line
from platform.wordobjects.baseobject import BaseObject
from platform.util.geometry import aabb_colision, prism, plane_least_rows
from platform.util.packets import send_block, send_color

from twisted.internet.task import callLater


class Platform(BaseObject):
    label = None
    last_z = None
    target_z = None
    frozen = False
    mode = None
    busy = False
    running = False
    delay_call = None
    bound_triggers = None

    def __init__(self, protocol, id, x1, y1, z1, x2, y2, z2, color):
        BaseObject.__init__(self, protocol, id)
        self.label = str(self.id)
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.z, self.start_z = z1, z2
        self.height = self.start_z - self.z
        self.color = color
        for x, y, z in prism(x1, y1, z1, x2, y2, z2):
            protocol.map.set_point(x, y, z, color)

    def contains(self, x, y, z):
        return aabb_colision(x, y, z, self.x1, self.y1, self.z, self.x2, self.y2, self.start_z)

    def overlaps(self, p):
        return (self.x1 <= p.x2 and self.y1 <= p.y2 and self.z <= p.start_z and
                self.x2 >= p.x1 and self.y2 >= p.y1 and self.start_z >= p.z)

    def destroy(self):
        self.destroy_z(self.z, self.start_z + 1)
        self.release()

    def release(self):
        BaseObject.release(self)
        if self.bound_triggers:
            bound_buttons = set()
            for trigger in self.bound_triggers[:]:
                bound_buttons.add(trigger.parent)
                trigger.unbind()
            for button in bound_buttons:
                button.trigger_check()
        if self.delay_call and self.delay_call.active():
            self.delay_call.cancel()
        self.delay_call = None

    def start(self, height, mode, speed, delay, wait = None, force = False):
        if self.busy and not force:
            return
        if mode == 'raise':
            height = (self.start_z - self.z) + height
        elif mode == 'lower':
            height = (self.start_z - self.z) - height
        self.mode = mode
        self.last_z = self.z
        self.target_z = max(0, min(self.start_z, self.start_z - height))
        self.speed = speed
        self.wait = wait
        if self.z == self.target_z:
            return
        self.busy = True
        self.protocol.running_platforms.add(self)
        self.ticks_per_cycle = int(speed / UPDATE_FREQUENCY)
        self.ticks_left = self.ticks_per_cycle
        self.start_cycle_later(delay)

    def start_cycle_later(self, delay):
        self.running = False
        if self.delay_call and self.delay_call.active():
            self.delay_call.cancel()
        self.delay_call = None
        if delay > 0.0:
            self.delay_call = callLater(delay, self.run)
        else:
            self.run()

    def run(self):
        self.running = True
        self.protocol.running_platforms.add(self)

    def cycle(self):
        if self.frozen:
            return
        if self.z > self.target_z:
            self.z -= 1
            self.build_plane(self.z)
            self.protocol.update_entities()
            # unstuck players
            for player in self.protocol.players.itervalues():
                obj = player.world_object
                if obj is None:
                    continue
                looking_up = obj.orientation.get()[2] < 0.4 # 0.5 (allow lag)
                x, y, z = obj.position.get()
                if aabb_colision(x, y, z, self.x1, self.y1, self.z - 2, self.x2, self.y2, self.start_z):
                    if looking_up and not obj.crouch and not z > self.z:
                        # player is looking up, no need to readjust
                        continue
                    z = self.z - 2.4
                    if player.world_object.crouch:
                        z += 1.0
                    position_data = PositionData()
                    position_data.x = x
                    position_data.y = y
                    position_data.z = z
                    player.send_contained(position_data)
                    player.world_object.position.z = z
        elif self.z < self.target_z:
            self.destroy_z(self.z)
            self.protocol.update_entities()
            self.z += 1
        self.height = self.start_z - self.z
        if self.z == self.target_z:
            if self.mode == 'elevator':
                self.mode = 'return'
                self.target_z = self.last_z
                self.start_cycle_later(self.wait)
            else:
                self.busy = self.running = False
        if self.bound_triggers:
            for trigger in self.bound_triggers:
                trigger.callback(self)

    def build_line(self, x1, y1, z1, x2, y2, z2):
        line = cube_line(x1, y1, z1, x2, y2, z2)
        for x, y, z in line:
            self.protocol.map.set_point(x, y, z, self.color)
        block_line = BlockLine()
        block_line.player_id = 32
        block_line.x1 = x1
        block_line.y1 = y1
        block_line.z1 = z1
        block_line.x2 = x2
        block_line.y2 = y2
        block_line.z2 = z2
        self.protocol.send_contained(block_line, save=True)

    def build_plane(self, z):
        send_color(self.protocol, self.color)
        for line in plane_least_rows(self.x1, self.y1, self.x2, self.y2, z):
            self.build_line(*line)

    def destroy_z(self, z1, z2 = None):
        if z2 is None:
            z2 = z1 + 1
        protocol = self.protocol
        overlaps = [platform for platform in protocol.platforms.itervalues() if
                    platform is not self and platform.overlaps(self)]
        for x, y, z in prism(self.x1, self.y1, z1, self.x2, self.y2, z2):
            if any(platform.contains(x, y, z) for platform in overlaps):
                continue
            if (x, y, z) in protocol.buttons:
                continue
            if protocol.map.destroy_point(x, y, z):
                send_block(protocol, x, y, z, DESTROY_BLOCK)

    def serialize(self):
        z = self.last_z if self.mode == 'elevator' else self.target_z
        return {
            'id' : self.id,
            'start' : (self.x1, self.y1, z or self.z),
            'end' : (self.x2, self.y2, self.start_z),
            'label' : self.label,
            'color' : self.color,
            'frozen' : self.frozen
        }
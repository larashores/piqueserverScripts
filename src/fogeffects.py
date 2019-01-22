from twisted.internet.task import LoopingCall
from twisted.internet.reactor import callLater, seconds
from piqueserver.commands import command, get_player
from pyspades.color import interpolate_rgb
from pyspades.common import make_color, Vertex3
from pyspades.contained import GrenadePacket
from pyspades.server import fog_color
from pyspades.world import Grenade
from abc import abstractmethod, ABCMeta

S_SPECTATING = "{player} is spectating"
S_NOT_ALIVE = "{player} is waiting to respawn"
S_LIGHTNING = "{player} was struck by angry lightning!!!"
S_LIGHTNING_SELF = "You were struck down by angry lightning!!!"
S_LIGHTNING_IRC = "* {admin} called down lightning on {player}"

FOG_INTERVAL = 0.05

linear = lambda t: t
ease_out = quadratic = lambda t: t * t
ease_in = quadratic_inverse = lambda t: 1.0 - ((1.0 - t) ** 2)


@command('lightning')
def lightning(connection, name=None):
    # And I will strike down upon thee with great vengeance and furious anger
    # those who would attempt to poison and destroy My brothers

    protocol = connection.protocol
    if name:
        player = get_player(protocol, name)
        is_spectator = player.team and player.team.spectator
        if is_spectator:
            return S_SPECTATING.format(player=player.name)
        if player.hp < 0:
            return S_NOT_ALIVE.format(player=player.name)

        callLater(0.1, player.kill)
        callLater(0.1, create_explosion_effect_at_player, player)

        message = S_LIGHTNING.format(player=player.name)
        protocol.send_chat(message, sender=player)
        player.send_chat(S_LIGHTNING_SELF)
        if connection in protocol.players:
            message = S_LIGHTNING_IRC.format(admin=connection.name, player=player.name)
        else:
            message = '* ' + message
        protocol.irc_say(message)
    effects = [
        FogHold(protocol, 0.05, (0, 0, 0)),
        FogGradient(protocol, 0.8, (255, 255, 255), (0, 0, 0), ease_in),
        FogHold(protocol, 1.0, (0, 0, 0)),
        FogGradient(protocol, 4.0, (0, 0, 0), protocol.get_fog_effects_off_color, ease_out)
    ]
    protocol.run_fog_effects(effects)


@command('fade')
def fade(connection, r, g, b, time=1.0):
    color = (int(r), int(g), int(b))
    time = max(0.1, float(time))
    protocol = connection.protocol
    fade_time = time * 0.25
    effects = [
        FogGradient(protocol, fade_time, protocol.get_fog_effects_off_color, color, ease_in),
        FogHold(protocol, time, color),
        FogGradient(protocol, fade_time, color, protocol.get_fog_effects_off_color, ease_out)
    ]
    protocol.run_fog_effects(effects)


def create_explosion_effect_at_player(player):
    obj = player.world_object
    if obj is None:
        return
    protocol = player.protocol
    grenade = protocol.world.create_object(Grenade, 0.0, obj.position, None, Vertex3(), None)
    grenade_packet = GrenadePacket()
    grenade_packet.value = grenade.fuse
    grenade_packet.player_id = 32
    grenade_packet.position = grenade.position.get()
    grenade_packet.velocity = grenade.velocity.get()
    protocol.send_contained(grenade_packet)


class FogEffect(metaclass=ABCMeta):
    def __init__(self, protocol):
        self.protocol = protocol

    @abstractmethod
    def start(self):
        pass

    def end(self):
        self.stop()
        self.protocol.next_fog_effect()

    def stop(self):
        pass

    @staticmethod
    def wrap_if_necessary(func_or_value):
        return func_or_value if callable(func_or_value) else lambda: func_or_value


class FogHold(FogEffect):
    def __init__(self, protocol, duration, color):
        FogEffect.__init__(self, protocol)
        self.duration = duration
        self.color = self.wrap_if_necessary(color)
        self.call = None

    def start(self):
        if not self.call or not self.call.active():
            self.call = callLater(self.duration, self.end)
        self.protocol.set_fog_effects_on_color(self.color())

    def stop(self):
        if self.call and self.call.active():
            self.call.cancel()
        self.call = None


class FogSimple(FogEffect):
    def __init__(self, protocol, color):
        FogEffect.__init__(self, protocol)
        self.color = self.wrap_if_necessary(color)

    def start(self):
        self.protocol.set_fog_effects_on_color(self.color())
        self.end()


class FogGradient(FogEffect):
    def __init__(self, protocol, duration, begin, end, interpolator=linear):
        FogEffect.__init__(self, protocol)
        self.duration = duration
        self.begin_color = self.wrap_if_necessary(begin)
        self.end_color = self.wrap_if_necessary(end)
        self.interpolator = interpolator
        self.loop = LoopingCall(self.apply)
        self.complete = False

    def start(self):
        if not self.loop.running:
            self.final_time = seconds() + self.duration
            self.loop.start(FOG_INTERVAL, now=True)

    def stop(self):
        if self.loop.running:
            self.loop.stop()
        self.loop = None

    def get_color(self):
        t = 1.0 - (self.final_time - seconds()) / self.duration
        t = min(1.0, self.interpolator(t))
        return interpolate_rgb(self.begin_color(), self.end_color(), t)

    def apply(self):
        if self.complete:
            self.end()
            return
        self.protocol.set_fog_effects_on_color(self.get_color())
        self.complete = seconds() >= self.final_time


def apply_script(protocol, connection, config):
    class FogEffectProtocol(protocol):
        def __init__(self, *args, **kwargs):
            self._fog_effects = []
            self._fog_effects_off_color = protocol.fog_color
            self._fog_effects_on_color = protocol.fog_color
            protocol.__init__(self, *args, **kwargs)

        @property
        def fog_color(self):
            return self._fog_effects_on_color if self._fog_effects else self._fog_effects_off_color

        @fog_color.setter
        def fog_color(self, value):
            self._fog_effects_off_color = value

        def set_fog_color(self, color):
            if not self._fog_effects:
                protocol.set_fog_color(self, color)
            self._fog_effects_off_color = color

        def set_fog_effects_on_color(self, color):
            self._fog_effects_on_color = color
            if self._fog_effects:
                fog_color.color = make_color(*color)
                self.send_contained(fog_color, save=True)

        def get_fog_effects_off_color(self):
            return self._fog_effects_off_color

        def run_fog_effects(self, effects):
            self._clear_fog_effects()
            for effect in reversed(effects):
                self._fog_effects.append(effect)
            if self._fog_effects:
                self._fog_effects[-1].start()

        def next_fog_effect(self):
            self._fog_effects.pop(-1)
            if self._fog_effects:
                self._fog_effects[-1].start()

        def on_map_change(self, map_):
            self._clear_fog_effects()
            protocol.on_map_change(self, map_)

        def on_map_leave(self):
            self._clear_fog_effects()
            protocol.on_map_leave(self)

        def _clear_fog_effects(self):
            for fog_effect in self._fog_effects[:]:
                fog_effect.stop()
            self._fog_effects = []

    return FogEffectProtocol, connection

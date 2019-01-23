from pyspades.types import MultikeyDict
from piqueserver import cfg

from platform.commands.trigger.presstrigger import PressTrigger
from platform.commands.trigger.tracktrigger import TrackTrigger
from platform.commands.trigger.distancetrigger import DistanceTrigger
from platform.commands.trigger.heighttrigger import HeightTrigger
from platform.commands.action.platformaction import PlatformAction
from platform.commands.action.playeraction import PlayerAction
from platform.wordobjects.platform import Platform
from platform.wordobjects.button import Button

import json
import os
from twisted.internet.reactor import LoopingCall

DEFAULT_LOAD_DIR = os.path.join(cfg.config_dir, 'maps')
SAVE_ON_MAP_CHANGE = True
AUTOSAVE_EVERY = 0.0  # minutes, 0 = disabled

TRIGGER_CLASSES = {cls.type: cls for cls in (PressTrigger, TrackTrigger, DistanceTrigger, HeightTrigger)}
ACTION_CLASSES = {cls.type: cls for cls in (PlatformAction, PlayerAction)}


def platform_protocol(protocol):
    class PlatformProtocol(protocol):
        highest_id = None
        platforms = None
        platform_json_dirty = False
        running_platforms = None
        buttons = None
        position_triggers = None
        autosave_loop = None

        def on_map_change(self, map):
            self.highest_id = -1
            self.platforms = {}
            self.running_platforms = set()
            self.buttons = MultikeyDict()
            self.position_triggers = []
            self.platform_json_dirty = False
            self.load_platform_json()
            if AUTOSAVE_EVERY:
                self.autosave_loop = LoopingCall(self.dump_platform_json)
                self.autosave_loop.start(AUTOSAVE_EVERY * 60.0, now=False)
            protocol.on_map_change(self, map)

        def on_map_leave(self):
            if SAVE_ON_MAP_CHANGE:
                self.dump_platform_json()
            if self.autosave_loop and self.autosave_loop.running:
                self.autosave_loop.stop()
            self.autosave_loop = None
            for platform in self.platforms.itervalues():
                platform.release()
            for button in self.buttons.itervalues():
                button.release()
            self.platforms = None
            self.running_platforms = None
            self.buttons = None
            self.position_triggers = None
            protocol.on_map_leave(self)

        def on_world_update(self):
            for player in self.players.itervalues():
                for trigger in self.position_triggers:
                    trigger.callback(player)
            not_running = set()
            for platform in self.running_platforms:
                platform.ticks_left -= 1
                if platform.ticks_left <= 0:
                    platform.ticks_left = platform.ticks_per_cycle
                    platform.cycle()
                if not platform.running:
                    not_running.add(platform)
            self.running_platforms -= not_running
            protocol.on_world_update(self)

        def get_platform_json_path(self):
            filename = self.map_info.rot_info.full_name + '_platform.txt'
            return os.path.join(DEFAULT_LOAD_DIR, filename)

        def load_platform_json(self):
            path = self.get_platform_json_path()
            if not os.path.isfile(path):
                return
            with open(path, 'r') as file:
                data = json.load(file)
            ids = []
            for platform_data in data['platforms']:
                x1, y1, z1 = platform_data['start']
                x2, y2, z2 = platform_data['end']
                color = tuple(platform_data['color'])
                id = platform_data['id']
                ids.append(id)
                platform = Platform(self, id, x1, y1, z1, x2, y2, z2, color)
                platform.label = platform_data['label']
                platform.frozen = platform_data['frozen']
                self.platforms[id] = platform
            for button_data in data['buttons']:
                x, y, z = button_data['location']
                color = tuple(button_data['color'])
                id = button_data['id']
                ids.append(id)
                button = Button(self, id, x, y, z, color)
                button.label = button_data['label']
                button.logic = button_data['logic']
                button.cooldown = button_data['cooldown']
                button.disabled = button_data['disabled']
                button.silent = button_data['silent']
                for trigger_data in button_data['triggers']:
                    cls = trigger_data.pop('type')
                    new_trigger = TRIGGER_CLASSES[cls](self, **trigger_data)
                    new_trigger.parent = button
                    button.triggers.append(new_trigger)
                for action_data in button_data['actions']:
                    cls = action_data.pop('type')
                    new_action = ACTION_CLASSES[cls](self, **action_data)
                    button.actions.append(new_action)
                self.buttons[(id, (x, y, z))] = button
            ids.sort()
            self.highest_id = ids[-1] if ids else -1
            self.platform_json_dirty = True
            for button in self.buttons.itervalues():
                button.trigger_check()

        def dump_platform_json(self):
            if (not self.platforms and not self.buttons and
                    not self.platform_json_dirty):
                return
            data = {
                'platforms': [platform.serialize() for platform in
                              self.platforms.values()],
                'buttons': [button.serialize() for button in
                            self.buttons.values()]
            }
            path = self.get_platform_json_path()
            with open(path, 'w') as file:
                json.dump(data, file, indent=4)
            self.platform_json_dirty = True

        def get_platform(self, x, y, z):
            for platform in self.platforms.itervalues():
                if platform.contains(x, y, z):
                    return platform
            return None

        def is_platform(self, x, y, z):
            return self.get_platform(x, y, z) or (x, y, z) in self.buttons

    return PlatformProtocol

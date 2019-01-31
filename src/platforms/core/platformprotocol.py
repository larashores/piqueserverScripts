from pyspades.types import MultikeyDict
# from piqueserver.config import config

from platforms.worldobjects.trigger.presstrigger import PressTrigger
# from platforms.worldobjects.trigger.tracktrigger import TrackTrigger
# from platforms.worldobjects.trigger.distancetrigger import DistanceTrigger
# from platforms.worldobjects.trigger.heighttrigger import HeightTrigger
# from platforms.worldobjects.action.platformaction import PlatformAction
# from platforms.worldobjects.action.playeraction import PlayerAction
from platforms.worldobjects.platform import Platform
from platforms.worldobjects.button import Button
from platforms.util.geometry import prism_range
from playerstates.stateprotocol import state_protocol

import json
import os
from twisted.internet.task import LoopingCall

# DEFAULT_LOAD_DIR = os.path.join(config.config_dir, 'maps')
# SAVE_ON_MAP_CHANGE = True
# AUTOSAVE_EVERY = 0.0  # minutes, 0 = disabled
#
# TRIGGER_CLASSES = {cls.type: cls for cls in (PressTrigger, TrackTrigger, DistanceTrigger, HeightTrigger)}
# ACTION_CLASSES = {cls.type: cls for cls in (PlatformAction, PlayerAction)}


def platform_protocol(protocol):
    protocol = state_protocol(protocol)

    class PlatformProtocol(protocol):
        _next_id = 0

        def __init__(self, *args, **kwargs):
            self._buttons = MultikeyDict()
            self._platforms = {}
            self._distance_triggers = set()
            self._autosave_loop = LoopingCall(self.dump_platform_json)
            protocol.__init__(self, *args, **kwargs)

        def add_distance_trigger(self, trigger):
            self._distance_triggers.add(trigger)
            trigger.signal_remove.connect(self._distance_triggers.remove)

        def update_distance_triggers(self, player):
            for trigger in self._distance_triggers:
                trigger.update(player)

        def on_world_update(self):
            for player in self.players.values():
                self.update_distance_triggers(player)
            protocol.on_world_update(self)

        def create_button(self, location, color, label):
            if self.is_platform_or_button(location):
                return None
            button = Button(self, self._next_id, location, color, label)
            button.add_trigger(PressTrigger(self, False, button))
            self._buttons[(self._next_id, location)] = button
            self._next_id += 1
            return button

        def destroy_button(self, button):
            button.destroy()
            del self._buttons[button]
            for player in self.players.values():  # clear last button memory from players
                if player.last_button is button:
                    player.last_button = None

        def create_platform(self, location1, location2, z, color, label):
            for location in prism_range(*location1, z, *location2, z+1):
                if self.is_platform_or_button(location):
                    return None
            platform = Platform(self, self._next_id, location1, location2, z, color, label)
            self._platforms[self._next_id] = platform
            self._next_id += 1
            return platform

        def destroy_platform(self, platform):
            platform.destroy()
            del self._platforms[platform.id]
            for player in self.players.values():  # clear last platform memory from players
                if player.last_platform is platform:
                    player.last_platform = None

        def get_platform(self, location):
            for platform in self._platforms.values():
                if platform.contains(location):
                    return platform

        def get_button(self, location):
            if location in self._buttons:
                return self._buttons[location]

        def is_platform_or_button(self, location):
            return self.get_platform(location) or location in self._buttons

        # def on_map_change(self, map):
        #     self._next_id = 0
        #     self._platforms.clear()
        #     self._buttons.clear()
        #     self._distance_triggers.clear()
        #     self.load_platform_json()
        #     if AUTOSAVE_EVERY:
        #         self._autosave_loop.start(AUTOSAVE_EVERY * 60.0, now=False)
        #     protocol.on_map_change(self, map)
        #
        # def on_map_leave(self):
        #     if SAVE_ON_MAP_CHANGE:
        #         self.dump_platform_json()
        #     if self._autosave_loop.running:
        #         self._autosave_loop.stop()
        #     protocol.on_map_leave(self)
        #
        # def get_platform_json_path(self):
        #     filename = self.map_info.rot_info.full_name + '_platform.txt'
        #     return os.path.join(DEFAULT_LOAD_DIR, filename)
        #
        # def load_platform_json(self):
        #     path = self.get_platform_json_path()
        #     if not os.path.isfile(path):
        #         return
        #     with open(path, 'r') as file:
        #         data = json.load(file)
        #     ids = []
        #     for platform_data in data['platforms']:
        #         x1, y1, z1 = platform_data['start']
        #         x2, y2, z2 = platform_data['end']
        #         color = tuple(platform_data['color'])
        #         label = platform_data['label']
        #         id_ = platform_data['id']
        #         ids.append(id_)
        #         platform = Platform(self, id_, (x1, y1), (x2, y2), z1, color, label)
        #         platform.set_height(z2 - z1)
        #         platform.frozen = platform_data['frozen']
        #         self._platforms[id_] = platform
        #     for button_data in data['buttons']:
        #         location = button_data['location']
        #         color = tuple(button_data['color'])
        #         label = button_data['label']
        #         id_ = button_data['id']
        #         ids.append(id_)
        #         button = Button(self, id_, location, color, label)
        #         button.logic = button_data['logic']
        #         button.cooldown = button_data['cooldown']
        #         button.disabled = button_data['disabled']
        #         button.silent = button_data['silent']
        #         for trigger_data in button_data['triggers']:
        #             cls = TRIGGER_CLASSES[trigger_data.pop('type')]
        #             new_trigger = cls(self, button, **trigger_data)
        #             button.add_trigger(new_trigger)
        #         for action_data in button_data['actions']:
        #             cls = ACTION_CLASSES[action_data.pop('type')]
        #             new_action = cls(self, **action_data)
        #             button.add_action(new_action)
        #             self._platforms[id_].add_action(action_data)
        #         self._buttons[(id_, location)] = button
        #     self._next_id = max(ids) + 1 if ids else 0
        #     for button in self.buttons.values():
        #         button.trigger_check()
        #
        # def dump_platform_json(self):
        #     if not self._platforms and not self._buttons:
        #         return
        #     data = {
        #         'platforms': [platform.serialize() for platform in self.platforms.values()],
        #         'buttons': [button.serialize() for button in self.buttons.values()]
        #     }
        #     path = self.get_platform_json_path()
        #     with open(path, 'w') as file:
        #        json.dump(data, file, indent=4)

    return PlatformProtocol

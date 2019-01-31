"""
Script tool for progressively applying a large number of block changes to the map.

Usage:
    # At the top of the file
    import cbc
    
    # in your apply_script() function
    
    apply_script(protocol, connection, config)
        protocol, connection = cbc.apply_script(protocol, connection, config)
    
    # start
    generator = self.create_generator_function()
    
    handle = self.protocol.cbc_add(generator)
    # or
    handle = self.protocol.cbc_add(generator, update_interval, self.callback_function, *callback_args)
    
    # update_interval is the time (in seconds) between calls to `self.callback_function`
    
    # stop
    self.protocol.cbc_cancel(handle)

Callback receives these args:

    def callback_function(self, cbc_type, progress, total_elapsed_seconds, *callback_args):

The generator function should `yield <packets>, <progress>` for each unique packet sent to clients
Where packets is the number of packets sent this iteration, and progress is the current progress percentage

Author: infogulch
"""

from twisted.internet.task import LoopingCall
from enum import IntEnum
import time


TIME_BETWEEN_CYCLES = 0.06
MAX_UNIQUE_PACKETS = 30  # per 'cycle', each block op is at least 1
MAX_PACKETS = 300        # per 'cycle' cap for (unique packets * players)
MAX_TIME = 0.03          # max time each cycle takes


class _CbcInfo:
    def __init__(self, generator, update_interval, callback, callback_args):
        self.generator = generator
        self.update_interval = update_interval
        self.callback = callback
        self.callback_args = callback_args
        self.last_update = time.time()
        self.start = time.time()
        self.progress = 0


# note: client crashes when this goes over ~50
class ServerPlayer(object):
    server_players = set()
    
    def __init__(self):
        id_ = 33
        while id_ in ServerPlayer.server_players:
            id_ += 1
        self.player_id = id_
        ServerPlayer.server_players.add(id_)
    
    def __del__(self):
        ServerPlayer.server_players.discard(self.player_id)


def apply_script(protocol, connection, config):
    if hasattr(protocol, 'cbc_add'):
        return protocol, connection
    
    class CycleBlockCoiteratorProtocol(protocol):
        class CbcStatus(IntEnum):
            UPDATE = 0
            CANCELLED = 1
            FINISHED = 2
        
        def __init__(self, *args, **kwargs):
            self._cbc_running = False
            self._cbc_generators = {}
            self._cbc_call = LoopingCall(self._cbc_cycle)
            protocol.__init__(self, *args, **kwargs)
        
        def cbc_add(self, generator, update_time=10.0, callback=None, *args):
            info = _CbcInfo(generator, update_time, callback, args)
            handle = max(list(self._cbc_generators.keys()) + [0]) + 1
            self._cbc_generators[handle] = info
            if not self._cbc_running:
                self._cbc_running = True
                self._cbc_call.start(TIME_BETWEEN_CYCLES, False)
            return handle   # this handle lets you cancel in the middle later
        
        def cbc_cancel(self, handle):
            if handle in self._cbc_generators:
                info = self._cbc_generators[handle]
                if info.callback is not None:
                    info.callback(self.CbcStatus.CANCELLED, info.progress,
                                  time.time() - info.start, *info.callback_args)
                del self._cbc_generators[handle]
        
        def _cbc_cycle(self):
            sent_unique = sent_total = progress = 0
            current_handle = None
            cycle_time = time.time()
            while self._cbc_generators:
                try:
                    for handle, info in self._cbc_generators.items():
                        if (sent_unique > MAX_UNIQUE_PACKETS) or \
                           (sent_total > MAX_PACKETS) or \
                           (time.time() - cycle_time > MAX_TIME):
                            return
                        current_handle = handle
                        sent, progress = next(info.generator)
                        sent_unique += sent
                        sent_total += sent * len(self.players)
                        if time.time() - info.last_update > info.update_interval:
                            info.last_update = time.time()
                            info.progress = progress
                            if info.callback is not None:
                                info.callback(self.CbcStatus.UPDATE, progress, time.time() - info.start,
                                              *info.callback_args)
                except StopIteration:
                    info = self._cbc_generators[current_handle]
                    if info.callback is not None:
                        info.callback(self.CbcStatus.FINISHED, progress, time.time() - info.start, *info.callback_args)
                    del self._cbc_generators[current_handle]
            else:
                self._cbc_call.stop()
                self._cbc_running = False
        
        def on_map_change(self, map_):
            if hasattr(self, '_cbc_generators'):
                for handle in self._cbc_generators.keys():
                    self.cbc_cancel(handle)
            protocol.on_map_change(self, map_)
        
        def on_map_leave(self):
            if hasattr(self, '_cbc_generators'):
                for handle in self._cbc_generators.keys():
                    self.cbc_cancel(handle)
            protocol.on_map_leave(self)
    
    return CycleBlockCoiteratorProtocol, connection

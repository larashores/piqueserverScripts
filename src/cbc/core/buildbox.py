from pyspades.contained import BlockLine, SetColor
from pyspades.common import make_color
from pyspades.constants import *
from itertools import product
from cbc.core import cbc, util

# this file must be in the /scripts folder, but it is NOT included in config.txt

MAX_LINE_BLOCKS = 64


def ordered_product(ranges, order):
    """
    Iterates through ranges in the order specified in order, but each yield returns in the original order of the ranges
    """

    order_inv = zip(*sorted(zip(order, sorted(order))))[1]

    for prod in product(*(ranges[o] for o in order)):
        yield tuple(prod[o] for o in order_inv)


def build_filled_generator(protocol, x1, y1, z1, x2, y2, z2, color, god=False, god_build=False):
    # create a player instance, freed when the generator is done
    # other scripts that also use ServerPlayer won't get the same id!
    # this won't be necessary in 1.0
    splayer = cbc.ServerPlayer()

    line = BlockLine()
    line.player_id = splayer.player_id

    set_color = SetColor()
    set_color.value = make_color(*color)
    set_color.player_id = splayer.player_id
    protocol.send_contained(set_color, save=True)

    # check_protected = hasattr(protocol, 'protected')
    check_protected = False
    if god_build and protocol.god_blocks is None:
        protocol.god_blocks = set()

    map_ = protocol.map

    ranges = [range(min(x1, x2), max(x1, x2)+1),
              range(min(y1, y2), max(y1, y2)+1),
              range(min(z1, z2), max(z1, z2)+1)]

    order = zip(*sorted(zip([len(x) for x in ranges], [0, 1, 2])))[1]

    # set the first block position
    prod = ordered_product(ranges, order)
    line.x1, line.y1, line.z1 = prod.next()
    line.x2 = line.x1
    line.y2 = line.y1
    line.z2 = line.z1
    map_.set_point(line.x1, line.y1, line.z1, color)

    for x, y, z in prod:
        packets = 0
        if not god and check_protected and protocol.is_protected(x, y, z):
            continue
        if god_build:
            protocol.god_blocks.add((x, y, z))
        changed = (line.x1 != x or line.x2 != x) + (line.y1 != y or line.y2 != y) + (line.z1 != z or line.z2 != z)
        dist = abs(line.x1 - x) + abs(line.y1 - y) + abs(line.z1 - z)
        if changed > 1 or dist >= MAX_LINE_BLOCKS:
            protocol.send_contained(line, save=True)
            packets += 2
            line.x1 = x
            line.y1 = y
            line.z1 = z
        line.x2 = x
        line.y2 = y
        line.z2 = z
        map_.set_point(x, y, z, color)
        yield packets, 0

    protocol.send_contained(line, save=True)
    yield 1, 0


def build_filled(protocol, x1, y1, z1, x2, y2, z2, color, god=False, god_build=False):
    if util.invalid_range(x1, y1, z1) or util.invalid_range(x2, y2, z2):
        raise ValueError('Invalid coordinates: ({}, {}, {}):({}, {}, {})'.format(x1, y1, z1, x2, y2, z2))
    protocol.cbc_add(build_filled_generator(protocol, x1, y1, z1, x2, y2, z2, color))


def build_empty(protocol, x1, y1, z1, x2, y2, z2, color, god=False, god_build=False):
    build_filled(protocol, x1, y1, z1, x1, y2, z2, color, god, god_build)
    build_filled(protocol, x2, y1, z1, x2, y2, z2, color, god, god_build)
    build_filled(protocol, x1, y1, z1, x2, y1, z2, color, god, god_build)
    build_filled(protocol, x1, y2, z1, x2, y2, z2, color, god, god_build)
    build_filled(protocol, x1, y1, z1, x2, y2, z1, color, god, god_build)
    build_filled(protocol, x1, y1, z2, x2, y2, z2, color, god, god_build)

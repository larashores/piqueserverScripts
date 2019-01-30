from pyspades.contained import BlockAction, BlockLine, SetColor, PositionData, OrientationData
from pyspades.common import make_color
from pyspades.constants import BUILD_BLOCK, DESTROY_BLOCK


def send_color(protocol, color):
    set_color_packet = SetColor()
    set_color_packet.value = make_color(*color)
    set_color_packet.player_id = 32
    protocol.send_contained(set_color_packet, save=True)


def send_block(protocol, x, y, z, value=BUILD_BLOCK):
    if value == DESTROY_BLOCK and not protocol.map.destroy_point(x, y, z):
        return
    block_action_packet = BlockAction()
    block_action_packet.value = value
    block_action_packet.player_id = 32
    block_action_packet.x = x
    block_action_packet.y = y
    block_action_packet.z = z
    protocol.send_contained(block_action_packet, save=True)


def send_line(protocol, x1, y1, z1, x2, y2, z2):
    block_line = BlockLine()
    block_line.player_id = 32
    block_line.x1 = x1
    block_line.y1 = y1
    block_line.z1 = z1
    block_line.x2 = x2
    block_line.y2 = y2
    block_line.z2 = z2
    protocol.send_contained(block_line, save=True)


def send_position(player, x, y, z):
    position_data = PositionData()
    position_data.x = x
    position_data.y = y
    position_data.z = z
    player.send_contained(position_data)


def send_orientation(player, x, y, z):
    orientation_data = OrientationData()
    orientation_data.x = x
    orientation_data.y = y
    orientation_data.z = z
    player.send_contained(orientation_data)

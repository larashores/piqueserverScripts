from pyspades.contained import BlockAction, SetColor
from pyspades.common import make_color
from pyspades.constants import BUILD_BLOCK, DESTROY_BLOCK


def send_color(protocol, color):
    set_color_packet = SetColor()
    set_color_packet.value = make_color(*color)
    set_color_packet.player_id = 32
    protocol.send_contained(set_color_packet, save=True)


def send_block(protocol, x, y, z, value=BUILD_BLOCK):
    block_action_packet = BlockAction()
    block_action_packet.value = value
    block_action_packet.player_id = 32
    block_action_packet.x = x
    block_action_packet.y = y
    block_action_packet.z = z
    protocol.send_contained(block_action_packet, save=True)

from .mc_special_type import MCSpecialType
import io
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from minecraft.packet_reader import PacketReader


class Switch(MCSpecialType):
    @staticmethod
    def decode(stream: io.IOBase, structure: dict, packet: 'PacketReader'):
        if packet.id == 0x3a:
            pass
        # compare_value might be an int for example, and the fields we need to compare it to are always strings
        compare_value = packet.dict_relative_path_get(packet.data, packet.current_path, structure['compareTo'])
        if isinstance(compare_value, bool):  # special case for booleans, because python boolean starts with a capital letter
            compare_value = str(compare_value).lower()
        else:
            compare_value = str(compare_value)
        if compare_value in structure['fields'].keys():
            packet.decode_field(stream, structure['fields'][compare_value])

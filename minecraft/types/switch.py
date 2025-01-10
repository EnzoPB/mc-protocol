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
        compare_value = str(packet.dict_relative_path_get(packet.data, packet.current_path, structure['compareTo']))
        if compare_value in structure['fields'].keys():
            print(f'switch compare_value:{compare_value} field_type:{structure["fields"][compare_value]}')
            packet.decode_field(stream, structure['fields'][compare_value])

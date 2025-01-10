from .mc_special_type import MCSpecialType
import io
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from minecraft.packet_reader import PacketReader


class Container(MCSpecialType):
    @staticmethod
    def decode(stream: io.IOBase, structure: dict, packet: 'PacketReader'):
        for field_structure in structure:
            packet.current_path.append(field_structure['name'])  # enter into the path of this field
            print('container enter', field_structure['name'], packet.current_path)
            packet.decode_field(stream, field_structure['type'])  # decode this field, store its value into the data dict
            packet.current_path.pop()  # exit the path of this field
            print('container exit', field_structure['name'], packet.current_path)

from .mc_special_type import MCSpecialType
import io
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from minecraft.packet_reader import PacketReader


class Container(MCSpecialType):
    @staticmethod
    def decode(stream: io.IOBase, structure: dict, packet: 'PacketReader'):
        for field_structure in structure:
            if 'name' not in field_structure:
                field_structure['name'] = 'anon'  # TODO: what should the structure really be when is is anon?
            packet.current_path.append(field_structure['name'])  # enter into the path of this field
            packet.decode_field(stream, field_structure['type'])  # decode this field
            packet.current_path.pop()  # exit the path of this field, go on to the next one

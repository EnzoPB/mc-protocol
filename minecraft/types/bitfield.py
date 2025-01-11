from .mc_special_type import MCSpecialType
import io
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from minecraft.packet_reader import PacketReader


class BitField(MCSpecialType):
    @staticmethod
    def decode(stream: io.IOBase, structure: any, packet: 'PacketReader'):
        if packet.name == 'block_change':
            pass
        size = sum([field['size'] for field in structure])
        raw_bitfield = stream.read(size // 8)
        if len(raw_bitfield) != size//8:
            raise ValueError(f'bitfield size should be {size//8}, only got {len(raw_bitfield)}')
        bitfield = int.from_bytes(raw_bitfield)
        shift = size
        for field_structure in structure:
            packet.current_path.append(field_structure['name'])  # enter into the path of this field
            shift -= field_structure['size']
            val = (bitfield >> shift) & (1 << field_structure['size'] - 1)
            packet.dict_path_set(packet.data, packet.current_path, val)
            packet.current_path.pop()  # exit the path of this field

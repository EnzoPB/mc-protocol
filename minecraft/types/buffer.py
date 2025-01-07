from .mc_special_type import MCSpecialType
import io
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from minecraft.packet_reader import PacketReader


class Buffer(MCSpecialType):
    @staticmethod
    def encode(data: bytearray, data_part: list) -> bytearray:
        buffer = bytearray()
        from . import types_names  # import this here (not at top) to avoid circular import loop
        buffer.extend(types_names[data_part[1]['countType']].encode(len(data)))  # we add the length of the buffer, whose type can vary
        buffer.extend(data)
        return buffer

    @staticmethod
    def decode(stream: io.IOBase, structure: any, packet: 'PacketReader') -> bytearray:
        from . import types_names
        length = types_names[structure['countType']].decode(stream)
        data = stream.read(length)
        return bytearray(data)

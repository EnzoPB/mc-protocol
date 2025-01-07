from .mc_special_type import MCSpecialType
import io
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from minecraft.packet_reader import PacketReader


class Array(MCSpecialType):
    @staticmethod
    def decode(stream: io.IOBase, structure: dict, packet: 'PacketReader') -> list:
        # import this here (not at top) to avoid circular import loop
        from . import types_names

        # first we read the count (length of the array, depending on countType
        count = types_names[structure['countType']].decode(stream)
        array = []
        # decode each element of the array
        for i in range(count):
            array.append(packet.decode_field(stream, structure['type']))

        return array

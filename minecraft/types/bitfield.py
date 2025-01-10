from .mc_special_type import MCSpecialType
import io
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from minecraft.packet_reader import PacketReader


class BitField(MCSpecialType):
    @staticmethod
    def encode(data: bytearray, data_part: list) -> bytearray:
        if len(data) > 1:
            raise ValueError('BitField must be one byte long')
        return data

    @staticmethod
    def decode(stream: io.IOBase, structure: any, packet: 'PacketReader') -> bytearray:
        return bytearray(stream.read(1))

import io
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from minecraft.packet_reader import PacketReader

class MCSpecialType:  # only used for typing
    @staticmethod
    def encode(data: any, data_part: list) -> bytearray:
        pass

    @staticmethod
    def decode(stream: io.IOBase, structure: dict, packet: 'PacketReader') -> any:
        pass

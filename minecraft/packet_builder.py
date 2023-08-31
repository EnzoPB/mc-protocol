from .types import *
from typing import Type

class PacketBuilder:
    buffer: bytearray

    def __init__(self, packet_id: int) -> None:
        self.buffer = bytearray([packet_id])

    def set_structure(self, structure: list[tuple[any, Type[MCType]]]) -> None:
        # structure is a list of tuples with the format:
        # [
        #  (value, type class)
        # ]
        # for example:
        # [
        #  (123, VarInt)
        #  ({'test': True}, Json)
        # ]
        for item in structure:
            value = item[0]
            item_type = item[1]
            self.buffer.extend(item_type.encode(value))

    def get_final_data(self) -> bytearray:
        # add the size of the final data at the beginning of the packet (type varint)
        length = VarInt.encode(len(self.buffer))
        self.buffer = length + self.buffer
        return self.buffer

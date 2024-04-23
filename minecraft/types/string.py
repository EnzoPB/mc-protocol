from .mc_native_type import MCNativeType
from .varnum import VarInt
import io


class String(MCNativeType):
    @staticmethod
    def decode(stream: io.IOBase) -> str:
        length = VarInt.decode(stream)  # before every string, there is a varint containing its length
        return stream.read(length).decode()  # read the actual string and convert it to a string

    @staticmethod
    def encode(value: str) -> bytearray:
        buffer = bytearray()
        # add the string's length before the actual string
        length = VarInt.encode(len(value))
        buffer.extend(length)
        for char in value:
            buffer.extend(bytes([ord(char)]))
        return buffer

from .mc_native_type import MCNativeType
import struct
import io


class Float(MCNativeType):
    @staticmethod
    def encode(value: float) -> bytearray:
        return bytearray(struct.pack('>f', value))

    @staticmethod
    def decode(stream: io.IOBase) -> float:
        return struct.unpack('>f', stream.read(4))[0]


class Double:
    @staticmethod
    def encode(value: float) -> bytearray:
        return bytearray(struct.pack('>d', value))

    @staticmethod
    def decode(stream: io.IOBase) -> float:
        return struct.unpack('>d', stream.read(8))[0]

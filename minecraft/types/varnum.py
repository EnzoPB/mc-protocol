from .mc_native_type import MCNativeType
import struct
import io


class VarNum(MCNativeType):
    max_bytes: int

    @classmethod
    def decode(cls, stream: io.IOBase) -> int:
        shift = 0
        result = 0
        while True:
            i = stream.read(1)[0]
            result |= (i & 0x7f) << shift
            shift += 7
            if not (i & 0x80):
                return result

    @staticmethod
    def encode(value):
        out = bytes()
        while True:
            byte = value & 0x7F
            value >>= 7
            out += struct.pack("B", byte | (0x80 if value > 0 else 0))
            if value == 0:
                break
        return out


class VarInt(VarNum):
    max_bytes = 5


class VarLong(VarNum):
    max_bytes = 10

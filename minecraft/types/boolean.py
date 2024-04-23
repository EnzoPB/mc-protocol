from .mc_native_type import MCNativeType
import io


class Boolean(MCNativeType):
    @staticmethod
    def encode(value: bool) -> bytearray:
        return bytearray([value])

    @staticmethod
    def decode(stream: io.IOBase) -> bool:
        return stream.read(1) == 0x1

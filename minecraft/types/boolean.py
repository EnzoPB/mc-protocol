from .mc_native_type import MCNativeType
import io


class Boolean(MCNativeType):
    @staticmethod
    def encode(value: bool) -> bytearray:
        return bytearray([value])

    @staticmethod
    def decode(stream: io.IOBase) -> bool:
        value = stream.read(1)
        match value:
            case 0x1:
                return True
            case 0x0:
                return False
            case _:
                raise ValueError(f'Incorrect boolean value: {value}')

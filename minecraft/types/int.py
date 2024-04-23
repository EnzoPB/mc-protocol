from .mc_native_type import MCNativeType
import io


class Int(MCNativeType):
    size = 4  # size of the number type in bytes
    signed = True

    @classmethod
    def encode(cls, value: int) -> bytearray:
        return bytearray(value.to_bytes(cls.size, 'big', signed=cls.signed))

    @classmethod
    def decode(cls, stream: io.IOBase, signed: bool = True) -> int:
        return int.from_bytes(stream.read(cls.size), 'big', signed=cls.signed)


class UInt(Int):
    signed = False


class Byte(Int):
    size = 1


class UByte(Byte):
    signed = False


class Short(Int):
    size = 2


class UShort(Short):
    signed = False


class Long(Int):
    size = 8


class ULong(Long):
    signed = False

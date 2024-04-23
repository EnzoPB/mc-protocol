from .mc_native_type import MCNativeType
import io
import uuid


class UUID(MCNativeType):
    @staticmethod
    def decode(stream: io.IOBase) -> uuid.UUID:
        return uuid.UUID(bytes=stream.read(16))

    @staticmethod
    def encode(value: str | uuid.UUID) -> bytearray:
        if isinstance(value, str):
            return bytearray(uuid.UUID(value).bytes)
        elif isinstance(value, uuid.UUID):
            return bytearray(value.bytes)

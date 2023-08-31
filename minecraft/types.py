import io
import json
import struct
import uuid

class MCType:  # only used for typing
    @staticmethod
    def encode(value: any) -> bytearray:
        pass

    @staticmethod
    def decode(stream: io.IOBase) -> any:
        pass

class Boolean(MCType):
    @staticmethod
    def encode(value: bool) -> bytearray:
        return bytearray([value])

    @staticmethod
    def decode(stream: io.IOBase) -> bool:
        return stream.read(1) == 0x1

class Int(MCType):
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

class Float(MCType):
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


class VarNum(MCType):
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

class String(MCType):
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

class Json(MCType):
    @staticmethod
    def decode(stream: io.IOBase) -> dict:
        string = String.decode(stream)
        return json.loads(string)

    @staticmethod
    def encode(data: dict | list) -> bytearray:
        json_data = json.dumps(data)
        return String.encode(json_data)


class UUID(MCType):
    @staticmethod
    def decode(stream: io.IOBase) -> uuid.UUID:
        return uuid.UUID(bytes=stream.read(16))

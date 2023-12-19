import io
import json
import struct
import uuid

from .errors import *

class MCNativeType:  # only used for typing
    pass

class Boolean(MCNativeType):
    @staticmethod
    def encode(value: bool) -> bytearray:
        return bytearray([value])

    @staticmethod
    def decode(stream: io.IOBase) -> bool:
        return stream.read(1) == 0x1

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

class Json(MCNativeType):
    @staticmethod
    def decode(stream: io.IOBase) -> dict:
        string = String.decode(stream)
        return json.loads(string)

    @staticmethod
    def encode(data: dict | list) -> bytearray:
        json_data = json.dumps(data)
        return String.encode(json_data)


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


class MCSpecialType:  # only used for typing
    pass

class Option(MCSpecialType):  # optional field
    @staticmethod
    def encode(data: any, data_part: list):
        buffer = bytearray()
        # an optional field is composed of a boolean (is the data is defined or not?) and then the data, if it is defined
        if data is None:  # data is not defined
            return Boolean.encode(False)  # we only send false (the data is not defined)
        else:  # data is defined
            buffer.extend(Boolean.encode(True))  # yes, the data is defined
            data_type = types_names[data_part[1]]  # find the type corresponding to the data
            buffer.extend(data_type.encode(data))  # encode it into the buffer
            return buffer


def encode_field(data: dict, data_part: dict) -> bytearray:  # automatically decode a field
    if isinstance(data_part['type'], str):  # type can either be a string (native type)
        try:
            var_type = types_names[data_part['type']]  # get the corresponding type class
        except KeyError:
            raise UnknownType('Tried to decode unknown type: ' + data_part['type'])
        try:
            return var_type.encode(data[data_part['name']])
        except KeyError as e:
            raise InvalidPacketStructure(f'Cannot find key {e} in packet data')

    elif isinstance(data_part['type'], list):  # or type can be a list (more complex type)
        try:
            var_type = types_names[data_part['type'][0]]  # get the corresponding type class
        except KeyError:
            raise UnknownType('Tried to decode unknown type: ' + data_part['type'])
        try:
            return var_type.encode(data[data_part['name']], data_part['type'])
        except KeyError as e:
            raise InvalidPacketStructure(f'Cannot find key {e} in packet data')


types_names = {
    'bool': Boolean,
    'i8': Byte,
    'u8': UByte,
    'i16': Short,
    'u16': UShort,
    'i32': Int,
    'u32': UInt,
    'i64': Long,
    'u64': ULong,
    'f32': Float,
    'f64': Double,
    'varint': VarInt,
    'varlong': VarLong,
    'string': String,
    'json': Json,
    'UUID': UUID,

    'option': Option
}

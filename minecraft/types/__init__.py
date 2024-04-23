from .boolean import Boolean
from .int import Byte, UByte, Short, UShort, Int, UInt, Long, ULong
from .float import Float, Double
from .varnum import VarInt, VarLong
from .string import String
from .json import Json
from .uuid import UUID
from .option import Option

from ..errors import *

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
            raise InvalidPacketStructure(f'Cannot find key {e} in packet data', data)

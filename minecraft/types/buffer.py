from .mc_special_type import MCSpecialType
from .boolean import Boolean


class Buffer(MCSpecialType):  # optional field
    @staticmethod
    def encode(data: bytearray, data_part: list) -> bytearray:
        buffer = bytearray()
        from . import types_names, encode_field  # import this here (not at top) to avoid circular import loop
        buffer.extend(types_names[data_part[1]['countType']].encode(len(data)))  # we add the length of the buffer, whose type can vary
        buffer.extend(data)
        return buffer

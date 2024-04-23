from .mc_special_type import MCSpecialType
from .boolean import Boolean


class Option(MCSpecialType):  # optional field
    @staticmethod
    def encode(data: any, data_part: list) -> bytearray:
        buffer = bytearray()
        # an optional field is composed of a boolean (is the data is defined or not?) and then the data, if it is defined
        if data is None:  # data is not defined
            return Boolean.encode(False)  # we only send false (the data is not defined)
        else:  # data is defined
            from . import encode_field  # import this here (not at top) to avoid circular import loop
            buffer.extend(Boolean.encode(True))  # yes, the data is defined
            buffer.extend(encode_field(data, data_part[1]))
            return buffer

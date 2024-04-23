from .mc_special_type import MCSpecialType
from .boolean import Boolean


class Option(MCSpecialType):  # optional field
    @staticmethod
    def encode(data: any, data_part: list):
        buffer = bytearray()
        # an optional field is composed of a boolean (is the data is defined or not?) and then the data, if it is defined
        if data is None:  # data is not defined
            return Boolean.encode(False)  # we only send false (the data is not defined)
        else:  # data is defined
            from . import types_names  # we import this here to avoid circular imports loop
            buffer.extend(Boolean.encode(True))  # yes, the data is defined
            data_type = types_names[data_part[1]]  # find the type corresponding to the data
            buffer.extend(data_type.encode(data))  # encode it into the buffer
            return buffer

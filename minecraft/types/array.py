from .mc_special_type import MCSpecialType
import io


class Array(MCSpecialType):
    @staticmethod
    def decode(stream: io.IOBase, structure: dict) -> list:
        # import this here (not at top) to avoid circular import loop
        from . import types_names
        from ..packet_reader import PacketReader

        # first we read the count (length of the array, depending on countType
        count = types_names[structure['countType']].decode(stream)
        array = []
        # decode each element of the array
        for i in range(count):
            array.append(PacketReader.decode_field(stream, structure['type']))

        return array

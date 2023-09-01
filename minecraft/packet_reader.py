import io
import select
import zlib
from typing import Type

from .types import *

class PacketReader:
    def __init__(self, stream: io.IOBase, compression_threshold: int = -1) -> None:
        self.stream = stream
        # wait until there is data to read
        ready_to_read = False
        while not ready_to_read:
            ready_to_read = select.select([self.stream], [], [], 0.1)[0]

        length = VarInt.decode(self.stream)  # get the size of the packet

        data = self.stream.read(length)  # read the actual packet data
        while len(data) < length:  # sometimes the rest of the data hasn't been transmited yet
            data += stream.read(length - len(data))  # so we try to read what is missing

        self.stream = io.BytesIO(data)  # get the actual data, and store it as a stream

        if compression_threshold != -1:  # threshold of -1 means no compression
            data_length = VarInt.decode(self.stream)  # size of the uncompressed data
            if data_length != 0:  # if the packet is longer than the treshold, it is compressed
                decompressed_data = zlib.decompress(self.stream.read())
                if data_length != len(decompressed_data):
                    raise zlib.error('Incorrect uncompressed data length')
                self.stream = io.BytesIO(decompressed_data)  # rewrite a new stream with the uncompressed data

        self.id = VarInt.decode(self.stream)  # decode the packet id

    def set_structure(self, structure: dict[str, Type[MCType]]) -> None:
        # structure is a dict with the format:
        # {
        #  'field name': type class
        # }
        # for example:
        # {
        #  'field1': VarInt,
        #  'field2': Json
        # }
        for field_name in structure:
            # so for each field, we decode the data using the correct type and set it as an attribute for this class
            field_type = structure[field_name]
            value = field_type.decode(self.stream)
            setattr(self, field_name, value)

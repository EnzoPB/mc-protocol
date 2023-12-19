import io
import select
import zlib
from typing import Type
import minecraft_data

from .errors import UnknownPacket
from .types import *

class PacketReader:
    data: dict

    def __init__(self, stream: io.IOBase, state: str, compression_threshold: int = -1, mc_data: Type[minecraft_data.mod] = None) -> None:
        self.state = state
        self.stream = stream
        self.mc_data = mc_data
        self.data = {}

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
            print(data_length)
            if data_length != 0 and data_length >= compression_threshold:  # if the packet is longer than the treshold, it is compressed
                decompressed_data = zlib.decompress(self.stream.read())
                if data_length != len(decompressed_data):
                    raise zlib.error('Incorrect uncompressed data length')
                self.stream = io.BytesIO(decompressed_data)  # rewrite a new stream with the uncompressed data

        self.id = VarInt.decode(self.stream)  # decode the packet id

    name: str

    def decode(self) -> None:
        if self.mc_data is None and self.state is not None:
            return

        formatted_id = f'{self.id:#04x}'  # we need the id to be a string of format 0x00
        try:
            # get the packet name from its id
            self.name = self.mc_data.protocol[self.state]['toClient']['types']['packet'][1][0]['type'][1]['mappings'][formatted_id]
        except (ValueError, KeyError):  # failed to get the packet name
            raise UnknownPacket(f'Failed to get packet name from id {formatted_id}')

        try:
            # get the packet structure from its name
            structure = self.mc_data.protocol[self.state]['toClient']['types'][f'packet_{self.name}'][1]
            for field in structure:
                # if the type of the field is unknown, ignore the rest of the packet
                if type(field['type']) != str or field['type'] not in types_names:
                    raise UnknownPacket(f'Could not decode type {field["type"]}')

                self.decode_field(field)

        except (ValueError, KeyError):  # failed to get the packet name
            raise UnknownPacket(f'Failed to get packet structure from name {self.name} and id {formatted_id}')

        except (ValueError, KeyError):  # failed to get the packet, can be unknown, bad version or something else
            return

    def decode_field(self, structure: dict[str, str]) -> None:
        # structure is a dict with the format:
        # {
        #   'name': 'field name',
        #   'type': 'field type (see types.types_names)'
        # }
        # for example:
        # {
        #   'name': 'field1',
        #   'type': 'i64'
        # }
        value = types_names[structure['type']].decode(self.stream)
        setattr(self, structure['name'], value)
        self.data[structure['name']] = value

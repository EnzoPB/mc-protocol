import io
import select
import zlib
from typing import Type
import minecraft_data

from .types import *
from .errors import TimeoutReached


class PacketReader:
    data: dict

    def __init__(self, stream: io.IOBase, state: str, compression_threshold: int = -1, mc_data: Type[minecraft_data.mod] = None) -> None:
        self.state = state
        self.stream = stream
        self.mc_data = mc_data
        self.data = {}

        # wait until there is data to read
        ready = select.select([self.stream], [], [], 1)[0]
        if len(ready) == 0:
            raise TimeoutReached

        length = VarInt.decode(self.stream)  # get the size of the packet

        data = self.stream.read(length)  # read the actual packet data
        while len(data) < length:  # sometimes the rest of the data hasn't been transmited yet
            data += stream.read(length - len(data))  # so we try to read what is missing

        self.stream = io.BytesIO(data)  # get the actual data, and store it as a stream

        if compression_threshold != -1:  # threshold of -1 means no compression
            data_length = VarInt.decode(self.stream)  # size of the uncompressed data
            if data_length != 0 and data_length >= compression_threshold:  # if the packet is longer than the treshold, it is compressed
                decompressed_data = zlib.decompress(self.stream.read())
                if data_length != len(decompressed_data):
                    raise zlib.error('Incorrect uncompressed data length')
                self.stream = io.BytesIO(decompressed_data)  # rewrite a new stream with the uncompressed data

        self.id = VarInt.decode(self.stream)  # decode the packet id

    name: str

    def decode(self, structure: list = None) -> None:
        if self.mc_data is None and self.state is not None:
            return

        formatted_id = f'{self.id:#04x}'  # we need the id to be a string of format 0x00
        try:
            # get the packet name from its id
            self.name = self.mc_data.protocol[self.state]['toClient']['types']['packet'][1][0]['type'][1]['mappings'][formatted_id]
        except (ValueError, KeyError):  # failed to get the packet name
            raise UnknownPacket(f'Failed to get packet name from id {formatted_id}')

        try:
            if structure is None:
                # get the packet structure from its name
                structure = self.mc_data.protocol[self.state]['toClient']['types'][f'packet_{self.name}']

            field_value = PacketReader.decode_field(self.stream, structure)
            self.data = field_value

        except (ValueError, KeyError):  # failed to get the packet name
            raise UnknownPacket(f'Failed to get packet structure from name {self.name} and id {formatted_id}')

        except (ValueError, KeyError):  # failed to get the packet, can be unknown, bad version or something else
            return

    @staticmethod
    def decode_field(stream: io.IOBase, structure: str | list):
        # special type (container, array, buffer, etc...)
        # eg. structure = [
        #   'container',
        #   [
        #       {'name': 'field', type: 'varint'}
        #       {'name': 'field2', type: 'string'}
        #   ]
        # ]
        if isinstance(structure, list):
            if structure[0] in types_names:
                return types_names[structure[0]].decode(stream, structure[1])
            elif structure[0] == 'container':
                container = {}
                for field_structure in structure[1]:
                    container[field_structure['name']] = PacketReader.decode_field(stream, field_structure['type'])
                return container
            else:
                raise UnknownType(f'Could not decode type {structure[0]}')

        # native type (int, string, boolean, etc...)
        # eg. structure = 'i32'
        elif isinstance(structure, str):
            if structure in types_names:
                return types_names[structure].decode(stream)
            else:
                raise UnknownType(f'Could not decode type {structure}')

        else:
            raise InvalidPacketStructure(f'Invalid structure type "{type(structure)}"')


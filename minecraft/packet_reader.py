import io
import os.path
import select
import zlib
from typing import Type
import minecraft_data

from .types import *
from .errors import TimeoutReached


class PacketReader:
    data: dict

    def __init__(self,
                 stream: io.IOBase,
                 state: str,
                 compression_threshold: int = -1,
                 mc_data: Type[minecraft_data.mod] = None,
                 timeout: float = 1) -> None:
        self.state = state
        self.stream = stream
        self.mc_data = mc_data
        self.data = {}

        # wait until there is data to read
        ready = select.select([self.stream], [], [], timeout)[0]
        if len(ready) == 0:
            raise TimeoutReached('Timeout reached while reading')

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
    structure: any
    data = {}
    current_path = ''

    @staticmethod
    def dict_relative_path_get(dictionary: dict, path: str, relative_path: str) -> any:
        '''
        get a dictionnary value at a relative path

        usage:
            dict_relative_path_get({'a': {'b': 1, 'c': 2}}, 'a/b', '../c') -> 2
        '''
        absolute_path = os.path.normpath(os.path.join(path, relative_path))
        return PacketReader.dict_path_get(dictionary, absolute_path)

    @staticmethod
    def dict_path_get(dictionary: dict, path: str) -> any:
        '''
        get a dictionnary value at a path

        usage:
            dict_path_get({'a': {'b': 1}}, 'a/b') -> 1
        '''
        for item in path.split('/'):
            if item == '':
                return dictionary
            dictionary = dictionary[item]
        return dictionary

    @staticmethod
    def dict_path_set(dictionary: dict, path: str, value: any):
        '''
        sets a value in a dictionary using its path

        usage:
            dict_path_set({'a': {'b': 1}}, 'a/b', 2)
        '''
        path = path.split('/')
        key = path[-1]
        dictionary = PacketReader.dict_path_get(dictionary, '/'.join(path[:-1]))
        dictionary[key] = value

    def decode(self, structure: list = None) -> None:
        if self.mc_data is None and self.state is not None:
            return

        formatted_id = f'{self.id:#04x}'  # we need the id to be a string of format 0x00
        try:
            # get the packet name from its id
            self.name = self.mc_data.protocol[self.state]['toClient']['types']['packet'][1][0]['type'][1]['mappings'][formatted_id]
        except (IndexError, KeyError):  # failed to get the packet name
            raise UnknownPacket(f'Failed to get packet name from id {formatted_id}')

        try:
            if structure is None:
                # get the packet structure from its name
                structure = self.mc_data.protocol[self.state]['toClient']['types'][f'packet_{self.name}']
        except (IndexError, KeyError):  # failed to get the packet structure
            raise UnknownPacket(f'Failed to get packet structure from name {self.name} and id {formatted_id}')

        self.structure = structure
        self.decode_field(self.stream, structure)

    def decode_field(self, stream: io.IOBase, structure: str | list) -> None:
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
                self.dict_path_set(self.data, self.current_path, types_names[structure[0]].decode(stream, structure[1], self))
            elif structure[0] == 'switch':
                raise UnknownType('switch not implemented')
            elif structure[0] == 'container':
                for field_structure in structure[1]:
                    self.current_path = self.current_path + '/' + field_structure['name']  # enter into the path of this field
                    self.decode_field(stream, field_structure['type'])  # decode this field, store its value into the data dict
                    self.current_path = '/'.join(self.current_path.split('/')[:-1])  # exit the path of this field
            else:
                raise UnknownType(f'Could not decode type {structure[0]}')

        # native type (int, string, boolean, etc...)
        # eg. structure = 'i32'
        elif isinstance(structure, str):
            if structure in types_names:
                self.dict_path_set(self.data, self.current_path, types_names[structure].decode(stream))
            else:
                raise UnknownType(f'Could not decode type {structure}')

        else:
            raise InvalidPacketStructure(f'Invalid structure type "{type(structure)}"')


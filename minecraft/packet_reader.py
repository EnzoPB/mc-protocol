import io
import select
import zlib
from typing import Type
import minecraft_data

from . import types
from . import errors


class PacketReader:
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
        self.current_path = []

        # wait until there is data to read
        ready = select.select([self.stream], [], [], timeout)[0]
        if len(ready) == 0:
            raise errors.TimeoutReached('Timeout reached while reading')

        length = types.VarInt.decode(self.stream)  # get the size of the packet

        data = self.stream.read(length)  # read the actual packet data
        while len(data) < length:  # sometimes the rest of the data hasn't been transmited yet
            data += stream.read(length - len(data))  # so we try to read what is missing

        self.stream = io.BytesIO(data)  # get the actual data, and store it as a stream

        if compression_threshold != -1:  # threshold of -1 means no compression
            data_length = types.VarInt.decode(self.stream)  # size of the uncompressed data
            if data_length != 0 and data_length >= compression_threshold:  # if the packet is longer than the treshold, it is compressed
                decompressed_data = zlib.decompress(self.stream.read())
                if data_length != len(decompressed_data):
                    raise zlib.error('Incorrect uncompressed data length')
                self.stream = io.BytesIO(decompressed_data)  # rewrite a new stream with the uncompressed data

        self.id = types.VarInt.decode(self.stream)  # decode the packet id

    name: str
    structure: any


    def dict_relative_path_get(self, dictionary: dict, path: list, relative_path: str) -> any:
        '''
        get a dictionnary value at a relative path

        usage:
            dict_relative_path_get({'a': {'b': 1, 'c': 2}}, ['a', 'b'], '../c') -> 2
        '''
        abs_path = path.copy()
        relative_path = relative_path.split('/')
        relative_path.insert(0, '..')  # TODO: check if this is correct, compareTo paths are always 1 folder too deep
        for path_item in relative_path:
            if path_item == '..':
                if isinstance(abs_path[-1], int):
                    abs_path.pop()
                abs_path.pop()

            else:
                abs_path.append(path_item)
        # logique pas ok,
        return self.dict_path_get(dictionary, abs_path)

    def dict_path_get(self, dictionary: dict, path: list) -> any:
        '''
        get a dictionnary value at a path

        usage:
            dict_path_get({'a': {'b': 1}}, ['a', 'b']) -> 1
        '''
        result = dictionary.copy()
        for k in path:
            result = result[k]
        return result

    def dict_path_set(self, dictionary: dict, path: list, value: any):
        '''
        sets a value in a dictionary using its path

        usage:
            dict_path_set({'a': {'b': 1}}, ['a', 'b'], 2)
        '''
        result = dictionary
        for k in path[:-1]:  # Parcourt toutes les clés sauf la dernière
            if k not in result or not isinstance(result[k], dict):
                result[k] = {}  # Si une clé intermédiaire manque, crée un sous-dictionnaire
            result = result[k]
        result[path[-1]] = value  # Assigne la valeur à la clé finale

    def decode(self, structure: list = None) -> None:
        if self.mc_data is None and self.state is not None:
            return

        formatted_id = f'{self.id:#04x}'  # we need the id to be a string of format 0x00
        try:
            # get the packet name from its id
            self.name = self.mc_data.protocol[self.state]['toClient']['types']['packet'][1][0]['type'][1]['mappings'][formatted_id]
            print('name:', self.name)
        except (IndexError, KeyError):  # failed to get the packet name
            raise errors.UnknownPacket(f'Failed to get packet name from id {formatted_id}')

        try:
            if structure is None:
                # get the packet structure from its name
                structure = self.mc_data.protocol[self.state]['toClient']['types'][f'packet_{self.name}']
        except (IndexError, KeyError):  # failed to get the packet structure
            raise errors.UnknownPacket(f'Failed to get packet structure from name {self.name} and id {formatted_id}')

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
            if structure[0] in types.types_names:
                data = types.types_names[structure[0]].decode(stream, structure[1], self)
                if data is not None:
                    self.dict_path_set(self.data, self.current_path, data)
                # je pense que les arrays doivent etres ignorés dans le relative_get
                # dans le switch j'ai aussi le path qui change de recipes 0 data à recipes 0 type??
            else:
                raise errors.UnknownType(f'Could not decode type {structure[0]}')

        # native type (int, string, boolean, etc...)
        # eg. structure = 'i32'
        elif isinstance(structure, str):
            if structure in types.types_names:
                self.dict_path_set(self.data, self.current_path, types.types_names[structure].decode(stream))
            else:
                raise errors.UnknownType(f'Could not decode type {structure}')

        else:
            raise errors.InvalidPacketStructure(f'Invalid structure type "{type(structure)}"')


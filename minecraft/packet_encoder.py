from typing import Type
import minecraft_data

from .types import types_names, VarInt
from .errors import UnknownPacket, UnknownType, InvalidPacketStructure


def find_packet_id_from_name(packet_name: str, mc_data: Type[minecraft_data.mod], state: str) -> int:
    for id, name in mc_data.protocol[state]['toServer']['types']['packet'][1][0]['type'][1]['mappings'].items():
        if name == packet_name:
            return int(id, 16)


def encode_packet(packet: str | list[dict], data: dict, state: str, mc_data: Type[minecraft_data.mod]) -> bytearray:
    if isinstance(packet, str):
        try:
            packet_key = mc_data.protocol[state]['toServer']['types']['packet'][1][1]['type'][1]['fields'][packet]
            structure = mc_data.protocol[state]['toServer']['types'][packet_key][1]
        except KeyError:
            raise UnknownPacket('Tried to encode invalid packet: ' + packet)
        buffer = bytearray([find_packet_id_from_name(packet, mc_data, state)])
    else:
        structure = packet
        buffer = bytearray()

    for part in structure:
        try:
            var_type = types_names[part['type']]
        except KeyError:
            raise UnknownType('Tried to decode unknown type: ' + part['type'])

        try:
            buffer.extend(var_type.encode(data[part['name']]))
        except KeyError as e:
            raise InvalidPacketStructure(f'Cannot find key {e} in packet data')

    length = VarInt.encode(len(buffer))
    buffer = length + buffer
    return buffer
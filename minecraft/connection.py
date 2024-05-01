import socket
from typing import Type
import minecraft_data

minecraft_data.data_folder = 'minecraft-data/data'

from .errors import TimeoutReached
from .packet_reader import PacketReader
from .packet_encoder import encode_packet

class Connection:
    compression_threshold: int = -1  # compression disabled by default
    state: str
    mc_data: Type[minecraft_data.mod] = minecraft_data('1.20')

    def __init__(self, server_address: str, server_port: int = 25565, timeout: float = 1) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        try:
            self.socket.connect((server_address, server_port))
        except TimeoutError:
            raise TimeoutReached('Timeout reached while connecting')
        self.socket.settimeout(None)
        self.stream = self.socket.makefile('rb', 0)
        self.timeout = timeout

    def read_packet(self) -> PacketReader:
        return PacketReader(self.stream, self.state, self.compression_threshold, self.mc_data, self.timeout)

    def send_packet(self, packet: str | list[dict], data: dict = None) -> None:
        self.socket.send(encode_packet(packet, data, self.state, self.mc_data, self.compression_threshold))

    def set_protocol_version(self, protocol_version: int) -> None:
        # first we search for the minecraft version corresponding to the protocol version
        for version in minecraft_data.common().protocolVersions:
            if version['version'] == protocol_version:
                # once we found it we get the data corresponding to the minecraft version
                try:
                    self.mc_data = minecraft_data(version['minecraftVersion'])
                except KeyError:  # some versions are referenced by their major versions number only in minecraft-data, eg. 1.8.9 => 1.8
                    major_version = '.'.join(version['minecraftVersion'].split('.')[:-1])
                    self.mc_data = minecraft_data(major_version)
                return

        raise UnsupportedVersionError(f'Minecraft protocol version {protocol_version} is not supported')

    def close(self) -> None:
        self.socket.close()


class UnsupportedVersionError(Exception):
    pass

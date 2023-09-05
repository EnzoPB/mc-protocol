import socket
from typing import Type
import minecraft_data

from .packet_builder import PacketBuilder
from .packet_reader import PacketReader

class Connection:
    compression_threshold: int = -1  # compression disabled by default
    state: str
    mc_data: Type[minecraft_data.mod] | None = None

    def __init__(self, server_address: str, server_port: int = 25565) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_address, server_port))
        self.stream = self.socket.makefile('rb', 0)

    def send(self, packet: PacketBuilder) -> None:
        data = packet.get_final_data()
        self.socket.send(data)

    def read_packet(self) -> PacketReader:
        return PacketReader(self.stream, self.state, self.compression_threshold, self.mc_data)

    def set_protocol_version(self, protocol_version: int) -> None:
        # first we search for the minecraft version corresponding to the protocol version
        for version in minecraft_data.common().protocolVersions:
            if version['version'] == protocol_version:
                # once we found it we get the data corresponding to the minecraft version
                self.mc_data = minecraft_data(version['minecraftVersion'])
                return

        raise UnsupportedVersionError(f'Minecraft protocol version {protocol_version} is not supported')

    def close(self) -> None:
        self.socket.close()


class UnsupportedVersionError(Exception):
    pass

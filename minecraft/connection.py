import socket

from .packet_builder import PacketBuilder
from .packet_reader import PacketReader

class Connection:
    def __init__(self, server_address: str, server_port: int = 25565) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_address, server_port))
        self.stream = self.socket.makefile('rb', 0)

    def send(self, packet: PacketBuilder) -> None:
        data = packet.get_final_data()
        self.socket.send(data)

    def read_packet(self) -> PacketReader:
        return PacketReader(self.stream)

    def close(self) -> None:
        self.socket.close()

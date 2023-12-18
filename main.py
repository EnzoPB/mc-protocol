from minecraft.packet_builder import PacketBuilder
from minecraft.packet_reader import InvalidPacket
from minecraft.connection import Connection
from minecraft.types import *


if __name__ == '__main__':
    conn = Connection('localhost')
    conn.state = 'status'

    # status handshake packet
    hs = PacketBuilder(0x00)  # packet id
    hs.set_structure([
        (0, VarInt),  # protocol version (0 for ping)
        ('domain', String),  # address (can be anything)
        (25565, Short),  # port (can be anything)
        (1, VarInt)  # next state (1 for status)
    ])
    conn.send(hs)

    # status request packet
    req = PacketBuilder(0x00)  # packet id
    conn.send(req)

    status = conn.read_packet()
    status.decode_field({
        'name': 'json_data',
        'type': 'json'
    })

    protocol = status.json_data['version']['protocol']

    # we have to re-open a new connection to initiate the login state
    conn.close()

    conn = Connection('localhost')
    conn.set_protocol_version(protocol)
    conn.state = 'login'

    # login handshake packet
    hs = PacketBuilder(0x00)  # packet id
    hs.set_structure([
        (protocol, VarInt),  # protocol version (that we got from the status request)
        ('domain', String),  # address (can be anything)
        (25565, UShort),  # port (can be anything)
        (2, VarInt)  # next state (2 for login)
    ])
    conn.send(hs)

    # login packet
    login = PacketBuilder(0x00)  # packet id
    login.set_structure([
        ('Notch', String),  # username
        #(False, Boolean),  # has sig data
        (False, Boolean)  # has player uuid
    ])
    conn.send(login)

    while True:
        packet = conn.read_packet()
        try:
            packet.decode()
        except InvalidPacket as e:
            print(e)


        print(packet.data)

        if packet.id == 0x02 and conn.state == 'login':
            conn.state = 'play'

        if packet.id == 0x03 and conn.state == 'login':  # set compression
            conn.compression_threshold = packet.threshold

    conn.close()

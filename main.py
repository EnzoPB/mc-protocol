from minecraft.packet_builder import PacketBuilder
from minecraft.connection import Connection
from minecraft.types import *


if __name__ == '__main__':
    conn = Connection('enzopb.me')

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
    status.set_structure({
        'json_data': Json
    })

    protocol = status.json_data['version']['protocol']

    # we have to re-open a new connection to initiate the login state
    conn.close()

    conn = Connection('enzopb.me')

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
        ('Notch', String)  # username
    ])
    conn.send(login)

    while True:
        packet = conn.read_packet()
        if packet.id == 0x32:  # player info
            packet.set_structure({
                'action': VarInt
            })
            if packet.action == 0:  # add player
                packet.set_structure({
                    'number_of_players': VarInt,
                    'uuid': UUID,
                    'username': String
                })
                print(packet.uuid, packet.username)

    conn.close()

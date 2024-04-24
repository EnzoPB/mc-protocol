from minecraft.errors import UnknownPacket, InvalidPacketStructure
from minecraft.connection import Connection

import uuid


if __name__ == '__main__':
    conn = Connection('ddns.enzopb.me', 25566)
    conn.state = 'handshaking'

    # status handshake packet
    conn.send_packet('set_protocol', {
        'protocolVersion': 0,
        'serverHost': 'domain',
        'serverPort': 25565,
        'nextState': 1
    })

    conn.state = 'status'

    # status request packet
    conn.send_packet('ping_start', {})

    status = conn.read_packet()
    status.decode([{
        'name': 'response',
        'type': 'json'
    }])

    protocol = status.data['response']['version']['protocol']

    # we have to re-open a new connection to initiate the login state
    conn.close()

    conn = Connection('ddns.enzopb.me', 25566)
    conn.set_protocol_version(protocol)
    conn.state = 'handshaking'

    # login handshake packet
    conn.send_packet('set_protocol', {
        'protocolVersion': protocol,
        'serverHost': 'domain',
        'serverPort': 25565,
        'nextState': 2
    })

    conn.state = 'login'

    username = 'test'

    # generate player's UUID from username (offline mode)
    # equivalent of Java's nameUUIDFromBytes
    class OfflinePlayerNamespace:
        bytes = b'OfflinePlayer:'
    player_uuid = uuid.uuid3(OfflinePlayerNamespace, username)

    # login packet
    conn.send_packet('login_start', {
        'username': username,
        'playerUUID': player_uuid
    })

    while True:
        packet = conn.read_packet()
        try:
            packet.decode()
        except (UnknownPacket, InvalidPacketStructure) as e:
            print(e)

        print(packet.name, packet.data)

        if packet.name == 'disconnect' or packet.name == 'kick_disconnect':
            exit()

        if conn.state == 'play':
            if packet.name == 'keep_alive':
                conn.send_packet('keep_alive', {
                    'keepAliveId': packet.keepAliveId
                })

        if conn.state == 'login':
            if packet.name == 'compress':  # set compression
                conn.compression_threshold = packet.threshold
            if packet.name == 'success':
                conn.state = 'play'

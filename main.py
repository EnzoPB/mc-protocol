# This is a small example script that connects to a server,
# and then try to decode & log every packet it receives from the server,
# while sending keep alive packets to avoid getting kicked by the server

from minecraft.errors import UnknownPacket, InvalidPacketStructure, UnknownType
from minecraft.connection import Connection

import uuid
import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 main.py username host [port]\nExample: python3 main.py bot 127.0.0.1 25565')
    username = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 25565

    conn = Connection(host, port)
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
    # custom packet structure, otherwise the response is interpreted as string, and we have to decode json manually
    status.decode(['container', [{
        'name': 'response',
        'type': 'json'
    }]])

    protocol = status.data['response']['version']['protocol']

    # we have to re-open a new connection to initiate the login state
    conn.close()

    conn = Connection(host, port, timeout=3)
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


    respawned = False
    while True:
        packet = conn.read_packet()
        try:
            packet.decode()
        except (UnknownPacket, InvalidPacketStructure, UnknownType) as e:
            print(e)

        print(packet.name, packet.data)

        if packet.name == 'disconnect' or packet.name == 'kick_disconnect':
            exit()

        if conn.state == 'play':
            if packet.name == 'keep_alive':
                conn.send_packet('keep_alive', {
                    'keepAliveId': packet.data['keepAliveId']
                })
            if not respawned:
                respawned = True
                conn.send_packet('client_command', {
                    'actionId': 0
                })

        if conn.state == 'login':
            if packet.name == 'compress':  # set compression
                conn.compression_threshold = packet.data['threshold']
            if packet.name == 'success':
                if protocol >= 764:  # >= 1.20.2
                    conn.send_packet('login_acknowledged')
                    conn.state = 'configuration'
                else:
                    conn.state = 'play'

        if conn.state == 'configuration':  # >= 1.20.2
            if packet.name == 'finish_configuration':
                conn.send_packet('finish_configuration')
                conn.state = 'play'

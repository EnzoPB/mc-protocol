from minecraft.errors import UnknownPacket
from minecraft.connection import Connection


if __name__ == '__main__':
    conn = Connection('localhost')
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
    status.decode_field({
        'name': 'json_data',
        'type': 'json'
    })

    protocol = status.data['json_data']['version']['protocol']

    # we have to re-open a new connection to initiate the login state
    conn.close()

    conn = Connection('localhost')
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

    # login packet
    conn.send_packet('login_start', {
        'username': 'caca',
        'playerUUID': 'be3370e3-ad3d-4635-aaf7-f7165668e8fc'
    })

    while True:
        packet = conn.read_packet()
        try:
            packet.decode()
        except UnknownPacket as e:
            print(e)

        print(packet.name, packet.data)

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

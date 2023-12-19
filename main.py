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
    conn.send_packet([
        {'type': 'varint', 'name': 'id'},
        {'type': 'string', 'name': 'username'},
        {'type': 'bool', 'name': 'hasuuid'}
    ], {
        'id': 0x00,
        'username': 'Notch',
        'hasuuid': False
    })


    while True:
        packet = conn.read_packet()
        try:
            packet.decode()
        except UnknownPacket as e:
            print(e)

        print(packet.data)

        if packet.id == 0x02 and conn.state == 'login':
            conn.state = 'play'

        if packet.id == 0x03 and conn.state == 'login':  # set compression
            conn.compression_threshold = packet.threshold

    conn.close()

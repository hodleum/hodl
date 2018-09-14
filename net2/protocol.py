from .config import *
from .models import *
from .server import Server, peer, protocol

log = logging.getLogger(__name__)

server = Server(PORT)


@server.handle('share_peers', 'request')
def share_peers():
    peers = [
        {
            'key': _peer.pub_key,
            'address': _peer.addr
        } for _peer in session.query(Peer).filter('Peer.pub_key').all()
    ]
    peer.send(Message(
        'request',
        request='peers',
        data=peers
    ))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO,
                        format='%(name)s.%(funcName)-20s [LINE:%(lineno)-3s]# [{}] %(levelname)-8s [%(asctime)s]'
                               '  %(message)s'.format('<Bob>'))

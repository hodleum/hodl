from .config import *
from .models import *
from .server import Server, peer, protocol

log = logging.getLogger(__name__)

server = Server(PORT)


@server.handle('share_peers', 'request')
def share_peers():
    peers = [_peer.dump() for _peer in session.query(Peer).all()]
    peer.send(Message(
        'request',
        request='peers',
        data={
            'peers': peers
        }
    ))


@server.handle('share_users', 'request')
def share_users():
    users = [user.dump() for user in session.query(User).all()]
    peer.send(Message(
        'request',
        request='users',
        data={
            'users': users,
        }
    ))


@server.handle('new_user', 'request')
def record_new_user(key, name):
    user = session.query(User).filter_by(name=name)
    if not user:
        user = User(pub_key=key, name=name)
        with lock:
            session.add(user)
            session.commit()
        protocol.send_all(Message(
            'request',
            request='new_user',
            data=user.dump()
        ))


@server.handle('peers', 'request')
def record_peers(peers):
    with lock:
        for data in peers:
            if not session.query(Peer).filter_by(addr=data['address']):
                new_peer = Peer(protocol.copy(), pub_key=data['key'], addr=data['address'])
                session.add(new_peer)  # TODO: test new peers
        session.commit()


@server.handle('users', 'request')
def record_users(users):
    with lock:
        for data in users:
            if not session.query(User).filter_by(name=data['name']):
                new_user = Peer(protocol.copy(), pub_key=data['key'], name=data['name'])
                session.add(new_user)
        session.commit()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO,
                        format='%(name)s.%(funcName)-20s [LINE:%(lineno)-3s]# [{}] %(levelname)-8s [%(asctime)s]'
                               '  %(message)s'.format('<Bob>'))

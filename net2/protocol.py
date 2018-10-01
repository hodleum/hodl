from .config import *
from .models import *
from .server import peer, protocol, server


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO,
                    format='%(name)s.%(funcName)-20s [LINE:%(lineno)-3s]# [{}] %(levelname)-8s [%(asctime)s]'
                           '  %(message)s'.format('<Bob>'))


@server.handle('share_peers', 'request')
def share_peers():
    peers = [_peer.dump() for _peer in session.query(Peer).all()]
    peer.request(Message(
        name='peers',
        data={
            'peers': peers
        }
    ))


@server.handle('share_users', 'request')
def share_users():
    users = [_user.dump() for _user in session.query(User).all()]
    peer.request(Message(
        name='users',
        data={
            'users': users,
        }
    ))


@server.handle('new_user', 'request')
def record_new_user(key, name):
    new_user = session.query(User).filter_by(name=name)
    if not new_user:
        new_user = User(protocol, public_key=key, name=name)
        protocol.add_object(new_user)
        protocol.send_all(Message(
            name='new_user',
            data=new_user.dump()
        ))


@server.handle('peers', 'request')
def record_peers(peers):
    with lock:
        for data in peers:
            if not session.query(Peer).filter_by(addr=data['address']):
                new_peer = Peer(protocol, public_key=data['key'], addr=data['address'])
                session.add(new_peer)  # TODO: test new peers
        session.commit()


@server.handle('users', 'request')
def record_users(users):
    with lock:
        for data in users:
            if not session.query(User).filter_by(name=data['name']):
                new_user = Peer(protocol, public_key=data['key'], name=data['name'])
                session.add(new_user)
        session.commit()


if __name__ == '__main__':
    pass

from .models import *
from .server import peer, protocol, server


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
def record_new_user(key: str, name: str):
    new_user = session.query(User).filter_by(name=name).first()
    if not new_user:
        new_user = User(protocol, public_key=key, name=name)
        session.add(new_user)
        session.commit()
        protocol.send_all(Message(
            name='new_user',
            data=new_user.dump()
        ))


@server.handle('peers', 'request')
def record_peers(peers: List[Dict[str, str]]):
    with lock:
        for data in peers:
            if not session.query(Peer).filter_by(addr=data['address']).first():
                new_peer = Peer(protocol, addr=data['address'])
                session.add(new_peer)  # TODO: test new peers
        session.commit()


@server.handle('users', 'request')
def record_users(users: List[Dict[str, str]]):
    with lock:
        for data in users:
            if not session.query(User).filter_by(name=data['name']):
                new_user = Peer(protocol, public_key=data['key'], name=data['name'])
                session.add(new_user)
        session.commit()


@server.handle('ping', 'request')
def ping():
    pass


if __name__ == '__main__':
    server.run()

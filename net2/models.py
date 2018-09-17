from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from threading import RLock
import time
import json
import logging
from .errors import *

log = logging.getLogger(__name__)
engine = create_engine('sqlite:///db.sqlite', echo=False, connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()
lock = RLock()


class TempDict(dict):
    update = 5
    expire = 60

    def __init__(self, *args):
        self.last_check = time.time()
        super().__init__(*args)

    def __setitem__(self, key, value):
        self.check()
        super().__setitem__(key, {
            'time': time.time(),
            'value': value
        })

    def __getitem__(self, item):
        self.check()
        return super().__getitem__(item)['value']

    def check(self):
        if time.time() - self.last_check < self.update:
            return
        for key, value in self.copy().items():
            if time.time() - value['time'] >= self.expire:
                del self[key]


class Message:
    """Message protocol"""

    def __init__(self, message_type, data=None, request=None, encoding=None,
                 tunnel_id=None, mid=None, forward=None, callback=None):
        self.type = message_type
        self.data = data
        self.request = request
        self.encoding = encoding
        self.id = mid
        self.forward = forward
        self.callback = callback
        self.tunnel_id = tunnel_id  # TODO: addressee

    @classmethod
    def from_bytes(cls, message: bytes):
        try:
            message = json.loads(message.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise BadRequest
        message_type = message.get('type')
        if not message_type:
            raise BadRequest('Missing message type')
        if message_type == 'request':
            request = message.get('request')

            if not request:
                raise BadRequest('Missing request')
            return cls(message_type, request=request, data=message.get('data'), callback=message.get('callback'))

        elif message_type == 'message':
            mid = message.get('id')
            if not mid:
                raise BadRequest('Missing message id')

            return cls(message_type, data=message.get('data'), encoding=message.get('encoding'), mid=mid,
                       forward=message.get('forward'), callback=message.get('callback'),
                       tunnel_id=message.get('tunnel_id'))

        elif message_type == 'shout':
            sender = message.get('sender')
            mid = message.get('id')

            if not sender:
                raise TypeError('Sender required')

            if not sender.get('uid') or not sender.get('subnet'):
                raise TypeError('Bad address')

            if not mid:
                raise TypeError('Missing message id')

            return cls(message_type, data=message.get('data'), encoding=message.get('encoding'), mid=mid,
                       forward=message.get('forward'), callback=message.get('callback'))
        elif message_type == 'error':
            return cls(message_type, data=message.get('data'), callback=message.get('callback'))
        raise TypeError('Bad message type')

    def dump(self) -> dict:
        if self.type == 'request':
            message = {
                'type': 'request',
                'request': self.request,
                'data': self.data,
            }
        elif self.type == 'message':
            message = {
                'type': 'message',
                'data': self.data,
                'encoding': self.encoding,
                'id': self.id
            }
        else:
            raise BadRequest('Bad message type')
        if self.forward:
            message['forward'] = self.forward
        if self.callback:
            message['callback'] = self.callback
        return json.dumps(message).encode('utf-8')

    def __str__(self):
        return json.dumps(self.dump())

    def __repr__(self):
        return f'<Message> {self.type} {self.data}'


class Peer(Base):
    __tablename__ = 'peers'

    addr = Column(String, primary_key=True)
    pub_key = Column(String)

    def __init__(self, proto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proto = proto

    def copy(self):
        return self

    def send(self, message: Message):
        log.debug(f'{self}: Send {message}')
        self.proto._send(message, self.addr)

    def dump(self):
        return {
            'key': self.pub_key,
            'address': self.addr
        }

    def __repr__(self):
        return f'<Peer {self.addr}>'


class User(Base):
    __tablename__ = 'users'

    pub_key = Column(String)
    name = Column(String, primary_key=True)

    def __init__(self, proto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proto = proto

    def send(self, message: Message):
        log.debug(f'{self}: Send {message}')
        self.proto.send(message, self.name)

    def dump(self):
        return {
            'key': self.pub_key,
            'name': self.name
        }


class Tunnels(TempDict):
    expire = 6000

    def add(self, tunnel_id, backward_peer, forward_peer):
        self[tunnel_id] = [backward_peer, forward_peer]

    def send(self, message):
        peers = self.get(message.tunnel_id)
        if not peers:
            return
        peers[1]._send(message)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    session.commit()

from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from cryptogr import get_random, verify, sign, encrypt, decrypt
from threading import RLock
from .errors import *
import logging
import uuid
import attr
import time
import json

log = logging.getLogger(__name__)
engine = create_engine('sqlite:///db.sqlite', echo=False, connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()
lock = RLock()


class TempStructure:
    update_time = 5
    expire = 60

    def __init__(self):
        self.last_check = time.time()


class TempDict(dict, TempStructure):
    def __init__(self, *args):
        dict.__init__(self, *args)
        TempStructure.__init__(self)

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
        if time.time() - self.last_check < self.update_time:
            return
        for key, value in self.copy().items():
            if time.time() - value['time'] >= self.expire:
                del self[key]


@attr.s
class Message:
    """Message"""
    name = attr.ib(type=str)
    data = attr.ib(factory=dict)
    salt = attr.ib(type=str)

    @salt.default
    def _salt_gen(self):
        return get_random()

    @data.validator
    @name.validator
    def _check_type(self, attribute, value):
        if attribute.name == 'name' and not isinstance(value, str) or \
                attribute.name == 'data' and not isinstance(value, dict):
            raise BadRequest

    def dump(self):
        return attr.asdict(self)

    def to_json(self):
        return json.dumps(self.dump())

    @classmethod
    def from_json(cls, data):
        return cls(**json.loads(data))


@attr.s
class MessageWrapper:
    """Wrapper for message"""
    message = attr.ib(default=None)
    type = attr.ib(type=str, default='message')
    sender = attr.ib(type=str, default=None)
    encoding = attr.ib(default='json')
    id = attr.ib(type=str)
    sign = attr.ib(type=str, default=None)
    tunnel_id = attr.ib(type=str, default=None)
    callback = attr.ib(default=None)

    acceptable_types = ['message', 'request', 'shout']
    acceptable_encodings = ['json']

    @id.default
    def _id_gen(self):
        return str(uuid.uuid4())

    @classmethod
    def from_bytes(cls, wrapper: bytes):
        try:
            wrapper = json.loads(wrapper.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise BadRequest
        message_type = wrapper.get('type')
        if not message_type or message_type not in cls.acceptable_types:
            raise BadRequest('Wrong message type')
        sender = wrapper.get('sender')
        if message_type != 'request' and not sender or not \
                isinstance(sender, str):
            raise BadRequest('Sender name required')

        message = wrapper.get('message')
        if not message:
            raise BadRequest('Message required')
        encoding = wrapper.get('encoding')
        if encoding not in cls.acceptable_encodings:
            raise BadRequest('Bad encoding')
        uid = wrapper.get('id')
        if not uid or not isinstance(uid, str):
            raise BadRequest('Id required')
        signature = wrapper.get('sign')
        if message_type != 'request' and not signature or not \
                isinstance(signature, str):
            raise BadRequest('Sign required')
        tunnel_id = wrapper.get('tunnel_id')
        callback = wrapper.get('callback')
        if tunnel_id and not isinstance(tunnel_id, str) or \
                callback and type(callback) not in [str, int]:
            raise BadRequest('Are u idiot?')

        wrapper = cls(
            message_type,
            sender,
            encoding,
            uid,
            signature,
            tunnel_id,
            callback
        )
        return wrapper

    def encrypt(self, public_key):
        return encrypt(self.message.to_json(), public_key)

    def decrypt(self, private_key):
        self.message = json.loads(decrypt(self.message.to_json(), private_key))

    def create_sign(self, private_key):
        self.sign = sign(self.message.to_json(), private_key)

    def verify(self, public_key):
        if self.type == 'request':
            return
        if not verify(self.message.to_json(), self.sign, public_key):
            raise VerificationFailed('Bad sign')

    def prepare(self, private_key=None, public_key=None):
        assert self.type != 'request' or not self.sender
        if private_key and self.type != 'request':
            self.sign = sign(self.message.to_json(), private_key)
            self.message: Message = self.encrypt(public_key)

    def to_json(self):
        json.dumps(attr.asdict(self))


class Peer(Base):
    __tablename__ = 'peers'

    addr = Column(String, primary_key=True)

    def __init__(self, proto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proto = proto

    def copy(self):
        return self

    def send(self, wrapper: MessageWrapper):
        """
        Send prepared Message with wrapper to peer.

        WARNING! Don't try to send Message without wrapper.
        Use Peer.request
        """
        if isinstance(wrapper, Message):
            log.warning('`Peer.send` method for sending requests is deprecated! '
                        'Use `Peer.request` instead')
            return self.request(wrapper)
        self.proto._send(wrapper, self.addr)

    def request(self, message: Message):
        """
        Send request to Peer.

        WARNING! Requests are unsafe.
        Don't try to send private_key information via Peer.request
        """
        log.debug(f'{self}: Send request {message}')
        wrapper = MessageWrapper(message, 'request')
        self.proto._send(wrapper, self.addr)

    def dump(self):
        return {
            'address': self.addr
        }

    def __repr__(self):
        return f'<Peer {self.addr}>'


class User(Base):
    __tablename__ = 'users'

    public_key = Column(String)
    name = Column(String, primary_key=True)

    def __init__(self, proto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proto = proto

    def send(self, message: Message):
        log.debug(f'{self}: Send {message}')
        self.proto.send(message, self.name)

    def dump(self):
        return {
            'key': self.public_key,
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


def create_db():
    Base.metadata.create_all(engine)
    session.commit()


if __name__ == '__main__':
    create_db()

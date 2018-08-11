import time
import json
import logging
from .config import *
from .errors import *


log = logging.getLogger(__name__)


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
                 addressee=None, sender=None, mid=None, forward=None, callback=None):
        self.type = message_type
        self.data = data
        self.request = request
        self.encoding = encoding
        self.addressee = addressee
        self.sender = sender
        self.id = mid
        self.forward = forward
        self.callback = callback

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

            if DEBUG:
                assert not message.get('uid')
            return cls(message_type, request=request, data=message.get('data'), callback=message.get('callback'))

        elif message_type == 'message':
            addressee = message.get('addressee')
            sender = message.get('sender')
            mid = message.get('id')

            if not addressee:
                raise BadRequest('No addressee')

            if (not addressee.get('uid') or not addressee.get('subnet')) or (
                    sender and (not sender.get('uid') or not sender.get('subnet'))):
                raise BadRequest('Bad address')

            if not mid:
                raise BadRequest('Missing message id')

            if DEBUG:
                assert not message.get('address')

            return cls(message_type, data=message.get('data'), encoding=message.get('encoding'), addressee=addressee,
                       sender=sender, mid=mid, forward=message.get('forward'), callback=message.get('callback'))

        elif message_type == 'shout':
            sender = message.get('sender')
            mid = message.get('id')

            if not sender:
                raise TypeError('Sender required')

            if not sender.get('uid') or not sender.get('subnet'):
                raise TypeError('Bad address')

            if not mid:
                raise TypeError('Missing message id')

            return cls(message_type, data=message.get('data'), encoding=message.get('encoding'),
                       sender=sender, mid=mid, forward=message.get('forward'), callback=message.get('callback'))
        elif message_type == 'error':
            return cls(message_type, data=message.get('data'), callback=message.get('callback'))
        raise TypeError('Bad message type')

    def dump(self):
        """
        :return: dict
        """
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
                'addressee': self.addressee,
                'sender': self.sender,
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


class Peer:
    def __init__(self, addr, proto):
        self.ping_time = time.time()
        self.addr = addr
        self.proto = proto

    def copy(self):
        return self

    def send(self, message: Message):
        """
        Low level send to peer
        """
        if message.request != 'ping':
            log.debug(f'[Peer {self.addr}]: Send {message}')
        self.proto._send(message.dump(), self.addr)


class Tunnels(TempDict):
    expire = 600

    def add(self, tunnel_id, backward_peer, forward_peer):
        self[tunnel_id] = (backward_peer, forward_peer)

    def send(self, message):
        peers = self.get(message.tunnel_id)
        if not peers:
            return
        peers[1].send(message)

import time
import json
import string
from .config import *


def convert_base(num, to_base=10, from_base=10):
    if isinstance(num, str):
        n = int(num, from_base)
    else:
        n = int(num)
    alphabet = string.digits + string.ascii_lowercase
    if n < to_base:
        return alphabet[n]
    else:
        return convert_base(n // to_base, to_base) + alphabet[n % to_base]


class NetAddress(int):

    def get_nearest(self, goal: int, addresses: list) -> int:
        return min([goal - i for i in addresses if i <= self])


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
                 addressee=None, sender=None, mid=None, forward=None, callback=None, tunnel_id=None):
        self.type = message_type
        self.data = data
        self.request = request
        self.encoding = encoding
        self.addressee = addressee
        self.sender = sender
        self.id = mid
        self.forward = forward
        self.callback = callback
        self.tunnel_id = tunnel_id

    @classmethod
    def from_json(cls, message):
        """
        :param message: json
        :type message: str

        :return: Message
        """
        message = json.loads(message)
        message_type = message.get('type')
        if not message_type:
            raise TypeError('Missing message type')
        if message_type == 'request':
            request = message.get('request')

            if not request:
                raise TypeError('Missing request')

            if DEBUG:
                assert not message.get('uid')
            return cls(message_type, request=request, data=message.get('data'), callback=message.get('callback'))

        elif message_type == 'message':
            addressee = message.get('addressee')
            sender = message.get('sender')
            mid = message.get('id')
            tunnel_id = message.get('tunnel_id')

            if not addressee:
                raise TypeError('No addressee')

            if (not addressee.get('uid') or not addressee.get('subnet')) or (
                    sender and (not sender.get('uid') or not sender.get('subnet'))):
                raise TypeError('Bad address')

            if not mid:
                raise TypeError('Missing message id')

            if sender and not tunnel_id:
                raise TypeError('Missing tunnel id')

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
        elif self.type == 'shout':
            message = {
                'type': 'shout',
                'data': self.data,
                'sender': self.sender,
                'encoding': self.encoding,
                'id': self.id
            }
        else:
            raise TypeError('Bad message type')
        if self.forward:
            message['forward'] = self.forward
        if self.callback:
            message['callback'] = self.callback
        return message

    def __str__(self):
        return json.dumps(self.dump())

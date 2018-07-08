import logging
import time
import json
# import random

from twisted.internet.protocol import DatagramProtocol
# from twisted.internet import task
from .config import *

log = logging.getLogger(__name__)


class Message:

    def __init__(self, message_type, data=None, request=None, encoding=None,
                 addressee=None, sender=None, address=None, mid=None):
        self.type = message_type
        self.data = data
        self.request = request
        self.encoding = encoding
        self.addressee = addressee
        self.sender = sender
        self.address = address
        self.id = mid

    @classmethod
    def from_json(cls, message):
        message = json.loads(message)
        message_type = message.get('type')
        if not message_type:
            raise TypeError('Missing message type')
        if message_type == 'request':
            request = message.get('request')
            address = message.get('address')

            if not request:
                raise TypeError('Missing request')
            if not address:
                raise TypeError('Request requires real address')
            if DEBUG:
                assert not message.get('uid')
            return cls(message_type, request=request, data=message.get('data'), address=address)

        elif message_type == 'message':
            addressee = message.get('addressee')
            sender = message.get('sender')
            mid = message.get('id')

            if not addressee:
                raise TypeError('No addressee')

            if (not addressee.get('uid') or not addressee.get('subnet')) or (
                    sender and (not sender.get('uid') or not sender.get('subnet'))):
                raise TypeError('Bad address')

            if not mid:
                raise TypeError('Missing message id')

            if DEBUG:
                assert not message.get('address')

            return cls(message_type, data=message.get('data'), encoding=message.get('encoding'), addressee=addressee,
                       sender=sender, mid=mid)

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
                       sender=sender, mid=mid)
        raise TypeError('Bad message type')

    def dump(self):
        if self.type == 'request':
            return {
                'type': 'request',
                'request': self.request,
                'data': self.data,
                'address': self.address
            }
        elif self.type == 'message':
            return {
                'type': 'message',
                'data': self.data,
                'addressee': self.addressee,
                'sender': self.sender,
                'encoding': self.encoding,
                'id': self.id
            }
        elif self.type == 'shout':
            return {
                'type': 'shout',
                'data': self.data,
                'sender': self.sender,
                'encoding': self.encoding,
                'id': self.id
            }
        raise TypeError('Bad message type')

    def __str__(self):
        return json.dumps(self.dump())


class PeerProtocol(DatagramProtocol):
    timeout = TIMEOUT
    update = UPDATE
    errors = {'001': 'Bad request', '002': 'Wrong request', '003': 'Connection first'}

    def __init__(self, ip, port, r, server):
        self.ip = ip
        self.port = port
        self.reactor = r
        self.server = server

        self.subnet = None
        self.parents_subnet = []
        self.children_subnet = []

        # self.reactor.callLater(0, lambda: task.LoopingCall(self.refresh_connections).start(self.update))

    def datagramReceived(self, datagram, addr):
        try:
            message = json.loads(datagram.decode('utf-8'))
            request = message.get('request')
            data = message.get('data')
            peer = self.server.peers.get(addr)
        except (UnicodeDecodeError, json.decoder.JSONDecodeError, TypeError):
            return self._send(self.get_error_message('001'), addr)

        if not peer and request != 'connect':
            return self._send(self.get_error_message('003'), addr)

        if request:
            if request != 'ping':
                log.debug('Datagram %s received from %s' % (repr(datagram), repr(addr)))

            if request == 'ping':
                peer = self.server.peers.get(addr)
                if not peer:
                    return self._send(self.get_error_message('003'), addr)
                peer.ping_time = time.time()

            elif request == 'connect':
                peer = self.server.peers.add(addr)
                if peer:
                    self.check_new_peers(data)
                    peer.connect(response=True)

            elif request == 'success_connect':
                peer = self.server.peers.get(addr)
                if peer:
                    self.check_new_peers(data)

    def get_error_message(self, error_id):
        return {'type': 'error', 'data': {'code': error_id, 'message': self.errors[error_id]}}

    def _send(self, data, address):
        if not data:
            return
        self.transport.write(json.dumps(data).encode('utf-8'), address)

    def forward(self, data):
        pass

    def send(self, data, net_address, uid):
        pass

    def check_new_peers(self, new_peers):
        new_peers = set([tuple(i) for i in new_peers])
        peers = new_peers - set(self.server.peers.keys())
        for addr in peers:
            peer = self.server.peers.add(addr)
            if peer:
                peer.connect()

    def refresh_connections(self):
        t = time.time()
        for peer in self.server.peers.copy().values():
            if t - peer.ping_time > self.timeout:
                peer.disconnect()
        self.server.peers.ping()


class Peer:
    def __init__(self, addr, proto):
        self.ping_time = time.time()
        self.addr = addr
        self.proto = proto

    def send(self, data):
        if data.get('request') != 'ping':
            log.debug('[Peer %s]: Send %s' % (self.addr, data))
        self.proto.send(data, self.addr)

    def ping(self):
        self.send({'request': 'ping'})

    def connect(self, response=False):
        self.send({
            'request': 'connect' if not response else 'success_connect',
            'data': list(self.proto.server.peers.keys())
        })

    def disconnect(self):
        log.info('[Peer %s]: connection lost' % (self.addr,))
        self.proto.server.peers.remove(self.addr)

    @staticmethod
    def on_message(message):
        log.info(message)
        return {'type': 'ok', 'data': 'ok'}


class SubNet(dict):
    max_size = SUB_NET_MAX_SIZE

    def __init__(self, proto, net_address, peers=()):
        self.proto = proto
        self.addr = net_address

        super().__init__()
        for addr in peers:
            self.add(addr)

    def add(self, addr):
        if addr in self or (self.proto.ip, self.proto.port) == tuple(addr) or len(self) >= self.max_size:
            return
        peer = Peer(addr, self.proto)
        self[addr] = peer
        return peer

    def remove(self, addr):
        if addr not in self:
            return
        return self.pop(addr)

    def ping(self):
        for peer in self.values():
            peer.ping()

    def shout(self, data):
        for peer in self.values():
            peer.send(data)


class Server:
    def __init__(self, ip='0.0.0.0', port=8000, white=True):
        from twisted.internet import reactor

        self.ip = ip
        self.port = port
        self.white = white

        self.reactor = reactor
        self.udp = PeerProtocol(ip, port, reactor, self)

        reactor.listenUDP(port, self.udp)

    def run(self):
        log.info('Start at %s:%s' % (self.ip, self.port))
        self.reactor.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO,
                        format='%(name)s.%(funcName)-20s [LINE:%(lineno)-3s]# [{}] %(levelname)-8s [%(asctime)s]'
                               '  %(message)s'.format('<Bob>'))
    s = Server()
    s.run()

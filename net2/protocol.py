import logging
import time
import json
import random

from twisted.internet.protocol import DatagramProtocol
# from twisted.internet import task
from .config import *
from .tools import TempDict

log = logging.getLogger(__name__)


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


class PeerProtocol(DatagramProtocol):

    timeout = TIMEOUT
    update = UPDATE
    max_children = MAX_CHILDREN_NET

    errors = {'001': 'Bad request', '002': 'Wrong request', '003': 'Connection first'}

    def __init__(self, ip, port, r, server):
        self.ip = ip
        self.port = port
        self.reactor = r
        self.server = server

        self.subnet = None
        self.parents_subnet = []
        self.children_subnet = []
        self.tunnels = Tunnels()

        self.waiting_for_connect = False

        # self.reactor.callLater(0, lambda: task.LoopingCall(self.refresh_connections).start(self.update))

    def datagramReceived(self, datagram, addr):
        if not self.subnet:
            return

        try:
            message = Message.from_json(datagram.decode('utf-8'))
        except (UnicodeDecodeError, json.decoder.JSONDecodeError, TypeError):
            return self._send(self.get_error_message('001'), addr)

        peer = self.subnet.get(addr)
        if not peer and message.request not in ['connect', 'invite']:
            return self._send(self.get_error_message('003'), addr)

        if message.type == 'request':
            if message.request != 'ping':
                log.debug('Datagram %s received from %s' % (repr(datagram), repr(addr)))
            else:
                if not peer:
                    return self._send(self.get_error_message('003'), addr)
                peer.ping_time = time.time()

            if message.request in ['connect', 'request_connect']:
                if message.request == 'request_connect':
                    addr = message.data['address']
                if self.subnet.has_place():
                    peer = self.subnet.add(addr)
                    if peer:
                        peer.invite()
                elif len(self.children_subnet) >= self.max_children:
                    random.choice(self.children_subnet).connect_request(addr)
                else:
                    self.create_child_subnet(addr)

            elif message.request == 'invite' and self.waiting_for_connect:
                self.subnet = SubNet(self, message.data['subnet'], peers=message.data['peers'])
                self.waiting_for_connect = False

        elif message.type == 'message':
            tunnel = self.tunnels.get(message.tunnel_id)
            if tunnel:
                tunnel.send(message)

            elif message.forward:
                self.forward(message)

    def get_error_message(self, error_id):
        """
        Get error message by id
        :param error_id: error code
        :type error_id: str

        :return: Message
        """

        return Message('error', data={'code': error_id, 'message': self.errors[error_id]}).dump()

    def _send(self, data, address):
        """
        Low level send
        """
        if not data:
            return
        self.transport.write(json.dumps(data).encode('utf-8'), address)

    def forward(self, message):
        """
        Send the package forward to net
        """
        message.forward //= 2
        peers = list(self.subnet.values()) + self.children_subnet + self.parents_subnet
        random.choice(peers).send(message)  # TODO: tunnel

    def send(self, message):
        """
        High level send
        :param message: data to send
        :return: None
        """
        pass

    def shout(self, message):
        """
        High level send to all peers
        :param message: data to send
        :return: None
        """
        pass

    def create_child_subnet(self, addr):
        pass

    def refresh_connections(self):
        t = time.time()
        for peer in self.subnet.copy().values():
            if t - peer.ping_time > self.timeout:
                peer.disconnect()
        self.subnet.ping()


class Peer:
    def __init__(self, addr, proto):
        self.ping_time = time.time()
        self.addr = addr
        self.proto = proto

    def send(self, message):
        """
        Low level send to peer
        :param message: data to send
        :return: None
        """
        if message.request != 'ping':
            log.debug('[Peer %s]: Send %s' % (self.addr, message))
        self.proto._send(message.dump(), self.addr)

    def ping(self):
        """
        Ping the peer
        :return: None
        """
        self.send(Message(
            message_type='request',
            request='ping'
        ))

    def connect(self):
        """
        Send connection request
        :return: None
        """
        self.send(Message(
            message_type='request',
            request='connect',
        ))
        self.proto.waiting_for_connect = True

    def connect_request(self, addr):
        """
        Resend connection request
        :param addr: address of child subnet
        :return: None
        """
        self.send(Message(
            message_type='request',
            request='connect_request',
            data={
                'address': addr
            }
        ))

    def invite(self):
        """
        Invite peer into subnet
        :return: None
        """
        self.send(Message(
            message_type='request',
            request='invite',
            data={
                'peers': list(self.proto.server.peers.keys()),
                'subnet': self.proto.subnet.addr
            }
        ))  # TODO: notify subnet

    def disconnect(self):
        """
        Forget peer
        :return: None
        """
        log.info('[Peer %s]: connection lost' % (self.addr,))
        self.proto.subnet.remove(self.addr)


class SubNet(dict):
    """SubNet class"""

    max_size = SUB_NET_MAX_SIZE

    def __init__(self, proto, net_address, peers=()):
        self.proto = proto
        self.addr = net_address

        super().__init__()
        for addr in peers:
            self.add(addr)

    def has_place(self):
        return len(self) < self.max_size

    def add(self, addr):
        """
        Add peer by address
        """
        if addr in self or (self.proto.ip, self.proto.port) == tuple(addr) or not self.has_place():
            return
        peer = Peer(addr, self.proto)
        self[addr] = peer
        return peer

    def remove(self, addr):
        """
        Remove peer by address
        """
        if addr not in self:
            return
        return self.pop(addr)

    def ping(self):
        """
        Ping subnet
        """
        for peer in self.values():
            peer.ping()

    def shout(self, data):
        """
        Shout into subnet
        """
        for peer in self.values():
            peer.send(data)


class Tunnels(TempDict):
    expire = 600

    def add(self, tunnel_id, forward_peer, backward_peer):
        self[tunnel_id] = (forward_peer, backward_peer)

    def send(self, message):
        peers = self.get(message.tunnel_id)
        if not peers:
            return
        peers[1].send(message)


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

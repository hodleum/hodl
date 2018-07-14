"""
Messages:

1) requests:
  --> Without connections
  --> You know real address
  --> Low level interaction

2) message:
  --> Connection required
  --> You don't know real address

"""


import logging
import time
import json
import random

from twisted.internet.protocol import DatagramProtocol
# from twisted.internet import task
from .config import *
from .tools import TempDict, Message, NetAddress

log = logging.getLogger(__name__)


class PeerProtocol(DatagramProtocol):
    timeout = TIMEOUT
    update = UPDATE
    max_children = MAX_CHILDREN_NET

    errors = {'001': 'Bad request', '002': 'Wrong request', '003': 'Connection required'}

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

        if addr not in self.subnet and message.type != 'request':
            return self._send(self.get_error_message('003'), addr)

        if message.type == 'request':
            peer = self.subnet.get(addr)
            if message.request != 'ping':
                log.debug('%s Datagram received %s' % (repr(addr), repr(datagram)))
            else:
                peer.ping_time = time.time()

            if message.request == 'connect':
                if self.subnet.has_place():
                    pass  # TODO: connect

            elif message.request == 'invite' and self.waiting_for_connect:
                self.subnet = SubNet(self, message.data['subnet'], peers=message.data['peers'])
                self.parents_subnet.append(Peer(addr, self))  # TODO: find another parent
                self.waiting_for_connect = False

        elif message.type == 'message':
            tunnel = self.tunnels.get(message.tunnel_id)
            if tunnel:
                tunnel.send(message)

            elif message.forward:
                self.forward(message)

    def get_error_message(self, error_id: str) -> dict:
        """
        Get error message by id
        :param error_id: error code
        """

        return Message('error', data={'code': error_id, 'message': self.errors[error_id]}).dump()

    def _send(self, data, address):
        """
        Low level send
        """
        if not data:
            return
        self.transport.write(json.dumps(data).encode('utf-8'), address)

    def forward(self, message: Message):
        """
        Send the package forward to net
        """
        message.forward //= 2
        peers = list(self.subnet.values()) + self.children_subnet + self.parents_subnet
        random.choice(peers).send(message)  # TODO: tunnel

    def send(self, message: Message):
        """
        High level send
        """
        pass

    def shout(self, message: Message):
        """
        High level send to all peers
        """
        pass

    def create_child_subnet(self, addr):
        peer = Peer(addr, self)
        self.children_subnet.append(peer)
        peer.create_subnet()  # TODO: notify subnet

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

    def send(self, message: Message):
        """
        Low level send to peer
        """
        if message.request != 'ping':
            log.debug('[Peer %s]: Send %s' % (self.addr, message))
        self.proto._send(message.dump(), self.addr)

    def ping(self):
        """
        Ping the peer
        """
        self.send(Message(
            message_type='request',
            request='ping'
        ))

    def connect(self):
        """
        Send connection request
        """
        self.send(Message(
            message_type='request',
            request='connect',
        ))
        self.proto.waiting_for_connect = True

    def connect_request(self, addr: tuple):
        """
        Resend connection request
        :param addr: address of child subnet
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
        """
        self.send(Message(
            message_type='request',
            request='invite',
            data={
                'peers': list(self.proto.server.peers.keys()),
                'subnet': self.proto.subnet.addr
            }
        ))  # TODO: notify subnet

    def create_subnet(self):
        address = self.proto.subnet.addr.copy()
        address[len(self.proto.children_subnet) - 1] += 1
        self.send(Message(
            message_type='request',
            request='invite',
            data={
                'peers': [],
                'subnet': address
            }
        ))

    def disconnect(self):
        """
        Forget peer
        """
        log.info('[Peer %s]: connection lost' % (self.addr,))
        self.proto.subnet.remove(self.addr)


class SubNet(dict):
    """SubNet class"""

    max_size = SUB_NET_MAX_SIZE

    def __init__(self, proto: PeerProtocol, net_address: NetAddress, peers=()):
        self.proto = proto
        self.addr = net_address

        self.children = []  # [SubNet(), ...]
        self.parents = []   # [SubNet(), ...]

        super().__init__()
        for addr in peers:
            self.add(addr)

    def has_place(self):
        return len(self) < self.max_size

    def has_children(self):
        return bool(self.children)

    def add(self, addr: tuple):
        """
        Add peer by address
        """
        if addr in self or (self.proto.ip, self.proto.port) == tuple(addr) or not self.has_place():
            return
        peer = Peer(addr, self.proto)
        self[addr] = peer
        return peer

    def remove(self, addr: tuple):
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

    def shout(self, message: Message):
        """
        Shout into subnet
        """
        for peer in self.values():
            peer.send(message)


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
    def __init__(self, ip=IP, port=PORT, white=True):
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

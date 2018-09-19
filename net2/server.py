from twisted.internet.protocol import DatagramProtocol
from collections import defaultdict
from .models import *
from werkzeug.local import Local
from .config import *
from .errors import *
import logging
import random


log = logging.getLogger(__name__)

local = Local()
peer = local['peer']
protocol = local['protocol']
user = local['user']


def error_cache(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except BaseError as ex:
            peer.send_error_message(ex)

    return wrapper


class PeerProtocol(DatagramProtocol):

    def __init__(self, server, r):
        self.reactor = r
        self.server = server

    def copy(self):
        return self

    @error_cache
    def datagramReceived(self, datagram: bytes, addr: tuple):
        # TODO: decryption
        message = Message.from_bytes(datagram)
        for func in self.server.handlers[message.type]:
            if func:
                func(message.data, self, addr, message.addressee)
        if not self.server.handlers[message.type]:
            raise UnhandledRequest

    def _send(self, data: Message, addr: tuple):
        """
        Low level send
        """
        if not data:
            return
        # TODO: encryption
        self.transport.write(data.dump(), addr)

    def send(self, message: Message, name: str):
        """
        High level send
        """
        pass

    def shout(self, message: Message):
        """
        High level send_all
        """

    @property
    def peers(self):
        peers = []
        for _peer in session.query(Peer).all():
            _peer.proto = self
            peers.append(_peer)
        return peers

    def send_all(self, message: Message):
        for _peer in self.peers:
            _peer.send(message)

    def random_send(self, message: Message):
        random.choice(self.peers).send(message)

    # TODO: refresh_connections(self):


class Server:
    request_handlers = defaultdict(lambda: [])
    handlers = defaultdict(lambda: [])
    on_open_func = None

    def __init__(self, port=PORT, white=True):
        from twisted.internet import reactor

        self.port = port
        self.white = white

        self.reactor = reactor
        self.udp = PeerProtocol(self, reactor)

        reactor.listenUDP(port, self.udp)

    def handle(self, event, _type='message'):
        if isinstance(event, str):
            event = list(event)

        def decorator(func):
            # noinspection PyUnresolvedReferences,PyDunderSlots
            def wrapper(message: Message, proto: PeerProtocol, addr: tuple, name=None):
                local.protocol = proto
                _peer = session.query(Peer).filter_by(addr=addr)
                if not _peer:
                    _peer = Peer(protocol, addr=addr)
                    _peer.send(Message('request', request='share_peers'))
                local.peer = _peer

                local.user = None
                if name:
                    local.user = session.query(User).filter_by(name=name).first()
                return func(message)
            for e in event:
                if _type == 'request':
                    self.request_handlers[e].append(wrapper)
                elif _type == 'message':
                    self.handlers[e].append(wrapper)
                else:
                    raise UnhandledRequest
            return func

        return decorator

    def run(self):
        log.info(f'Start at {self.port}')
        self.reactor.run()

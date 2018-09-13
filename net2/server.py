from twisted.internet.protocol import DatagramProtocol
from collections import defaultdict
from .models import *
from werkzeug.local import Local
from .config import *
from .errors import *
import logging


log = logging.getLogger(__name__)

local = Local()
peer = local['peer']
protocol = local['protocol']


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

        message = Message.from_bytes(datagram)
        for func in self.server.handlers[message.type]:
            if func:
                func(message.data, self, addr)
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

    def send(self, message: Message, addr: tuple):
        """
        High level send
        """
        pass

    @staticmethod
    def send_all(message: Message):
        for _peer in session.query(Peer).filter('Peer.pub_key').all():
            _peer.send(message)

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
        def decorator(func):
            # noinspection PyUnresolvedReferences,PyDunderSlots
            def wrapper(message: Message, proto: PeerProtocol, addr: tuple):
                local.protocol = proto
                _peer = session.query(Peer).filter_by(addr=addr)
                if not _peer:
                    _peer = Peer(protocol, addr=addr)
                    _peer.send(Message('request', request='share_peers'))
                local.peer = _peer
                return func(message)
            if _type == 'request':
                self.request_handlers[event].append(wrapper)
            if _type == 'message':
                self.handlers[event].append(wrapper)
            else:
                raise UnhandledRequest
            return func

        return decorator

    def run(self):
        log.info(f'Start at {self.port}')
        self.reactor.run()

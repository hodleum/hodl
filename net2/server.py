from twisted.internet.protocol import DatagramProtocol
# from twisted.internet import task
from .models import Message, Peer
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

        self.subnet = None
        self.parents_subnet = []
        self.children_subnet = []

        self.waiting_for_connect = False

        # self.reactor.callLater(0, lambda: task.LoopingCall(self.refresh_connections).start(self.update))

    def copy(self):
        return self

    @error_cache
    def datagramReceived(self, datagram: bytes, addr: tuple):

        message = Message.from_bytes(datagram)
        func = self.server.handlers.get(message.type)
        if func:
            func(message.data, self, addr)
        else:
            raise UnhandledRequest

    def _send(self, data: Message, addr: tuple):
        """
        Low level send
        """
        if not data:
            return
        self.transport.write(data.dump(), addr)

    def forward(self, message: Message):
        """
        Send the package forward to net
        """
        pass

    def send(self, message: Message):
        """
        High level send
        """
        pass

    def refresh_connections(self):
        pass


class Server:
    handlers = {}
    on_open_func = None

    def __init__(self, port=PORT, white=True):
        from twisted.internet import reactor

        self.port = port
        self.white = white

        self.reactor = reactor
        self.udp = PeerProtocol(self, reactor)

        reactor.listenUDP(port, self.udp)

    def handle(self, event):
        def decorator(func):
            # noinspection PyUnresolvedReferences,PyDunderSlots
            def wrapper(message: Message, proto: PeerProtocol, addr: tuple):
                local.protocol = proto
                local.peer = Peer(addr, proto)
                return func(message)

            self.handlers[event] = wrapper
            return wrapper

        return decorator

    def run(self):
        log.info(f'Start at {self.port}')
        self.reactor.run()

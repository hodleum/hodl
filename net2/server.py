"""

@server.handle('echo')
def echo(msg):
    user.send(Message('echo_response', {'msg': msg})


@server.handle('echo', 'request')
def echo_request:
    peer.request(Message('echo_response', {'msg': msg})


"""

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from collections import defaultdict
from typing import Callable
from .models import *
from werkzeug.local import Local
from cryptogr import gen_keys
from .config import *
from .errors import *
import logging
import random

log = logging.getLogger(__name__)

local = Local()
peer: Peer = local('peer')
user: User = local('user')


def error_cache(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except BaseError as _:
            log.exception('Exception during handling message.')

    return wrapper


class PeerProtocol(DatagramProtocol):

    def __init__(self, _server: 'Server', r: reactor):
        self.reactor = r
        self.server = _server

        self.name = 'name'  # TODO: name
        self.temp = TempDict()  # TODO: Temp set
        self.tunnels = TempDict()

        try:
            with open('net2/keys') as f:
                self.public, self.private_key = json.loads(f.read())
        except FileNotFoundError:
            self._gen_keys()

    def _gen_keys(self):
        self.private_key, self.public = gen_keys()
        with open('net2/keys', 'w') as f:
            f.write(json.dumps([self.public, self.private_key]))

    def copy(self) -> 'PeerProtocol':
        return self

    @staticmethod
    def add_object(obj: Any):
        """
        DEPRECATED! Use session.add and session.commit instead
        """
        with lock:
            session.add(obj)
            session.commit()

    @error_cache
    def datagramReceived(self, datagram: bytes, addr: tuple):
        wrapper = MessageWrapper.from_bytes(datagram)

        if wrapper.tunnel_id:
            if random.randint(0, 3) != random.randint(0, 3):  # TODO: safe random func
                return self.random_send(wrapper)  # TODO: Check exists tunnels
            wrapper.type = 'message'
            wrapper.tunnel_id = None

        if wrapper.id in self.temp:
            return
        else:
            self.temp[wrapper.id] = wrapper
            self._send_all(wrapper)

        for func in self.server.handlers[wrapper.type]:
            if func:
                func(wrapper, addr)
        if not self.server.handlers[wrapper.type]:
            raise UnhandledRequest

    def forward(self, message: MessageWrapper):
        pass  # TODO: forward message into tunnel

    def _send(self, data: MessageWrapper, addr: tuple):
        """
        Low level send
        """
        if not data:
            return
        self.transport.write(data.to_json().encode('utf-8'), addr)

    def send(self, message: Message, name: str, callback: T = None):  # TODO: callback handler
        """
        High level send
        """
        addressee: User = session.query(User).filter_by(name=name).first()
        wrapper = MessageWrapper(
            message,
            type='message',
            sender=self.name,
            tunnel_id=str(uuid.uuid4()),  # TODO: check exists tunnels
        )
        wrapper.callback = callback
        wrapper.prepare(self.private_key, addressee.public_key)
        self.random_send(wrapper)

    def shout(self, message: Message, callback: T = None):
        """
        High level send_all
        """
        wrapper = MessageWrapper(
            message,
            type='shout',
            sender=self.name,
            tunnel_id=str(uuid.uuid4())
        )
        wrapper.callback = callback
        self.random_send(wrapper)

    @property
    def peers(self) -> List[Peer]:
        # TODO: docstring
        peers = []
        for _peer in session.query(Peer).all():
            _peer.proto = self
            peers.append(_peer)
        return peers

    def send_all(self, message: Message):
        # TODO: docstring
        for _peer in self.peers:
            _peer.request(message)

    def _send_all(self, wrapper: MessageWrapper):
        for _peer in self.peers:
            _peer.send(wrapper)

    def random_send(self, wrapper: MessageWrapper):
        # TODO: docstring
        random.choice(self.peers).send(wrapper)


class Server:
    request_handlers = defaultdict(lambda: [])
    handlers = defaultdict(lambda: [])
    on_open_func = None

    def __init__(self, port: int = PORT, white: bool = True):
        from twisted.internet import reactor

        self.port = port
        self.white = white

        self.reactor = reactor
        self.udp = PeerProtocol(self, reactor)

        reactor.listenUDP(port, self.udp)

    def handle(self, event: S, _type: str = 'message') -> Callable:
        # TODO: docstring

        if isinstance(event, str):
            event = list(event)

        def decorator(func: Callable):
            # noinspection PyDunderSlots,PyUnresolvedReferences
            def wrapper(message_wrapper: MessageWrapper, addr: tuple):
                _peer = session.query(Peer).filter_by(addr=addr)
                if not _peer:
                    _peer = Peer(protocol, addr=addr)
                    _peer.request(Message('share_peers'))
                local.peer = _peer

                local.user = None
                if message_wrapper.sender:
                    local.user = session.query(User).filter_by(name=message_wrapper.sender).first()
                    if not local.user:
                        return

                    try:
                        message_wrapper.decrypt(proto.private)
                    except ValueError:
                        return

                return func(**message_wrapper.message.data)

            for e in event:
                if _type == 'request':
                    self.request_handlers[e].append(wrapper)
                elif _type == 'message':
                    self.handlers[e].append(wrapper)
                else:
                    raise UnhandledRequest
            return func

        return decorator

    def run(self, port: int = None):
        # TODO: docstring
        self.port = port if port else self.port
        log.info(f'Start at {self.port}')
        self.reactor.run()


server = Server(PORT)
protocol = server.udp

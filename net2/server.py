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
    name = Configs.name  # TODO: names

    def __init__(self, _server: 'Server', r: reactor):
        self.reactor = r
        self.server = _server

        self.temp = TempDict()  # TODO: Temp set
        self.tunnels = TempDict()

        try:
            with open(f'net2/{self.name}_keys') as f:
                self.public, self.private_key = json.loads(f.read())
        except FileNotFoundError:
            self._gen_keys()

    def _gen_keys(self):
        self.private_key, self.public = gen_keys()
        with open(f'net2/{self.name}_keys', 'w') as f:
            log.info(f'keys generated {self.name}')
            f.write(json.dumps([self.public, self.private_key]))

    def copy(self) -> 'PeerProtocol':
        return self

    def add_object(self, obj: Any):
        """
        DEPRECATED! Use session.add and session.commit instead
        """
        with lock:
            self.session.add(obj)
            self.session.commit()

    # noinspection PyUnresolvedReferences,PyDunderSlots
    @error_cache
    def datagramReceived(self, datagram: bytes, addr: tuple):

        addr = ':'.join(map(str, addr))
        log.debug(f'Datagram received {datagram}')
        wrapper = MessageWrapper.from_bytes(datagram)

        if wrapper.type != 'request':
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

        # Decryption message, preparing to process
        _peer = session.query(Peer).filter_by(addr=addr).first()
        if not _peer:
            _peer = Peer(protocol, addr=addr)
            _peer.request(Message('share_peers'))
            session.add(_peer)
            session.commit()
            log.debug(f'New peer {addr}')
        _peer.proto = self
        local.peer = _peer

        local.user = None
        if wrapper.sender:
            local.user = session.query(User).filter_by(name=wrapper.sender).first()
            if not local.user:
                return

            try:
                wrapper.decrypt(self.private)
            except ValueError:
                return

        for func in self.server.handlers[wrapper.type][wrapper.message.name]:
            if func:
                func(wrapper.message)
        if not self.server.handlers[wrapper.type][wrapper.message.name]:
            raise UnhandledRequest

    def forward(self, message: MessageWrapper):
        pass  # TODO: forward message into tunnel

    def _send(self, data: MessageWrapper, addr):
        """
        Low level send
        """
        if not data:
            return
        if isinstance(addr, str):
            addr: list = addr.split(':')
            addr[1] = int(addr[1])
            addr = tuple(addr)
        self.transport.write(data.to_json().encode('utf-8'), addr)

    def send(self, message: Message, name: str, callback: T = None):  # TODO: callback handler
        """
        High level send
        """
        addressee: User = self.session.query(User).filter_by(name=name).first()
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
    handlers = defaultdict(lambda: defaultdict(lambda: []))
    on_open_func = None

    def __init__(self, port: int = Configs.port, white: bool = True):
        from twisted.internet import reactor

        self.port = port
        self.white = white

        self.reactor = reactor
        self.udp = PeerProtocol(self, reactor)

        self.engine = None
        self.session = None

    def handle(self, event: S, _type: str = 'message') -> Callable:
        # TODO: docstring

        if isinstance(event, str):
            event = [event]

        def decorator(func: Callable):
            def wrapper(message: Message):
                return func(**message.data)

            for e in event:
                self.handlers[_type][e].append(wrapper)
            return func

        return decorator

    def run(self, port: int = None):
        # TODO: docstring

        self.port = port if port else self.port

        logging.basicConfig(level=logging.DEBUG if Configs.debug else logging.INFO,
                            format=f'%(name)s.%(funcName)-20s [LINE:%(lineno)-3s]# [{self.port}]'
                                   f' %(levelname)-8s [%(asctime)s]  %(message)s')

        self.reactor.listenUDP(self.port, self.udp)
        log.info(f'Started at {self.port}')
        self.reactor.run()


server = Server()
protocol = server.udp

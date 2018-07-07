import logging
import time
import json

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import task

log = logging.getLogger(__name__)


class Protocol(DatagramProtocol):
    timeout = 5
    update = 2
    errors = {'001': 'Bad request', '002': 'Wrong request', '003': 'Connection first'}

    def __init__(self, ip, port, r, server):
        self.ip = ip
        self.port = port
        self.reactor = r
        self.server = server
        self.reactor.callLater(1, lambda: task.LoopingCall(self.refresh_connections).start(self.update))
        self.reactor.callLater(1, lambda: task.LoopingCall(lambda: log.debug(self.server.peers.keys())).start(5))

    def datagramReceived(self, datagram, addr):
        try:
            message = json.loads(datagram.decode('utf-8'))
            request = message.get('request')
            data = message.get('data')
            peer = self.server.peers.get(addr)
        except (UnicodeDecodeError, json.decoder.JSONDecodeError):
            return self.send(self.get_error_message('001'), addr)

        if not peer and request != 'connect':
            return self.send(self.get_error_message('003'), addr)

        if request:
            if request != 'ping':
                log.debug('Datagram %s received from %s' % (repr(datagram), repr(addr)))

            if request == 'ping':
                peer = self.server.peers.get(addr)
                if not peer:
                    return self.send(self.get_error_message('003'), addr)
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

    def send(self, data, address):
        if not data:
            return
        self.transport.write(json.dumps(data).encode('utf-8'), address)

    def send_all(self, data, addresses):
        for addr in addresses:
            self.send(data, addr)

    def check_new_peers(self, new_peers):
        new_peers = set([tuple(i) for i in new_peers])
        peers = new_peers - set(self.server.peers.keys())
        for addr in peers:
            peer = self.server.peers.add(addr)
            if peer:
                peer.connect()

    def do_ping(self):
        for peer in self.server.peers.values():
            peer.ping()

    def refresh_connections(self):
        t = time.time()
        for peer in self.server.peers.copy().values():
            if t - peer.ping_time > self.timeout:
                peer.disconnect()
        self.do_ping()


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


class Peers(dict):
    def __init__(self, proto, peers=()):
        self.proto = proto
        super().__init__()
        for addr in peers:
            self.add(addr)

    def add(self, addr):
        if addr in self or (self.proto.ip, self.proto.port) == addr:
            return
        peer = Peer(addr, self.proto)
        self[addr] = peer
        return peer

    def remove(self, addr):
        if addr not in self:
            return
        return self.pop(addr)


class Server:
    def __init__(self, ip='0.0.0.0', port=8000, white=True, peers=(), new_peers=()):
        from twisted.internet import reactor

        self.ip = ip
        self.port = port

        self.reactor = reactor
        self.udp = Protocol(ip, port, reactor, self)
        self.peers = Peers(self.udp, peers=peers)

        if not white:
            reactor.callLater(1, lambda: self.udp.check_new_peers(new_peers))
        reactor.listenUDP(port, self.udp)

    def run(self):
        log.info('Start at %s:%s' % (self.ip, self.port))
        self.reactor.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s.%(funcName)-20s [LINE:%(lineno)-3s]# [{}] %(levelname)-8s [%(asctime)s]'
                               '  %(message)s'.format('<Bob>'))
    # s = Server(peers=[('127.0.0.1', 8003)])
    s = Server(port=8001, white=False, new_peers=[('127.0.0.1', 8000)])
    s.run()

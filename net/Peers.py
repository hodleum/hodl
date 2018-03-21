import json
from socket import socket
import random
import cryptogr as cg


class Peer:
    def __init__(self, addr, ip, port):
        self.addr = addr
        self.netaddr = (ip, port)

    def is_white(self, myaddrs):
        sock = socket()
        try:
            sock.connect(self.netaddr)
            sock.send(json.dumps({'pubkeys': [addr[0]], cg.sign(json.dumps({'request': ['peercheck', random.randint(0, 10000)]}), addr[1]]) for addr in myaddrs], 'request': ['peercheck', random.randint(0, 10000)]}).encode())
            sock.listen(1)
            conn = sock.accept()[0]
            data = b''
            while True:
                p = conn.recv(1024)
                data += p
                if not p:
                    break
            h = cg.h(data.decode('utf-8'))
            data = json.loads(data.decode('utf-8'))
            pubkeys = data['pubkeys']
            for pubkey, sign in pubkeys:
                if not cg.verify_sign(sign, h, pubkey):
                    pubkeys.remove([pubkey, sign])
            if self.addr in pubkeys:
                return True
            return False
        except:
            return False

class Peers(set):
    """
    Class for storing peers.
    It is a set of peers(class Peer)
    """
    def save(self, file):
        with open(file, 'w') as f:
            f.write(json.dumps([json.dumps(peer) for peer in list(self)]))

    def open(self, file):
        with open(file, 'r') as f:
            for peer in json.loads(f.read()):
                self.add(json.loads(peer))

    def srchbyaddr(self, addr):
        for p in self:
            if p.addr == addr:
                return p
        return False


def check_is_white_peer(ip, addr, myaddrs, port=5000):
    sock = socket()
    try:
        sock.connect((ip, port))
        sock.send(json.dumps({'pubkeys': myaddrs, 'request': 'peercheck', random.randint(0, 10000)}).encode())
        sock.listen(1)
        conn = sock.accept()[0]

        data = b''
        while True:
            p = conn.recv(1024)
            data += p
            if not p:
                break
        hdata = json.loads(data.decode('utf-8'))
        hdata.pop('pubkeys')
        h = cg.h(json.dumps(hdata))
        data = json.loads(data.decode('utf-8'))
        pubkeys = data['pubkeys']
        for pubkey, sign in pubkeys:
            if not cg.verify_sign(sign, h, pubkey):
                pubkeys.remove([pubkey, sign])
        if addr in pubkeys:
            return True
        return False
    except:
        return False

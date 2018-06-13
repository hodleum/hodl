"""
Here are classes InputConnection and Connection. They defines communication between peers.
"""
import json
import socket
from threading import Thread
import block
import cryptogr as cg
import struct

global bch
bch = block.Blockchain()


class SignError(Exception):
    pass


class ConnectionErr(Exception):
    pass


def get_many_blocks(minb, maxb):
    blocks = []
    return blocks


def handle_request(req):
    ans = []
    return ans


def get_smart_contracts_mem(ind, start=0, stop=-1):
    pass


class Proto:
    def __init__(self, conn):
        self.sock = conn

    def connect(self, addr):
        self.sock.connect(addr)

    def listen(self, i):
        self.sock.listen(i)

    def accept(self):
        return self.sock.accept()

    def close(self):
        self.sock.close()

    def bind(self, addr):
        self.sock.bind(addr)

    def recv(self):
        if not self.sock:
            return

        chunk = self.sock.recv(4)
        if len(chunk) < 4:
            return
        slen = struct.unpack('>L', chunk)[0]
        chunk = self.sock.recv(slen)
        while len(chunk) < slen:
            chunk = chunk + self.sock.recv(slen - len(chunk))
        return chunk

    def send(self, record):

        if not self.sock:
            return

        msg = json.dumps(record).encode('utf-8')
        slen = struct.pack('>L', len(msg))
        self.sock.sendall(slen + msg)


class Connection(Thread):
    """
    It is an output connection (First user in net's doc).
    """

    def __init__(self, ip, port, privkeys, pubkeys):
        self.privkeys = privkeys
        self.pubkeys = pubkeys

        self.sock = None
        self.conn = None

        super().__init__(target=self.connect, args=(ip, port))

    def connect(self, ip, port=5000):
        self.sock = Proto(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.sock.connect((ip, port))
        data = {'len(bch)': len(bch), 'lb': str(bch[-1])}
        h = cg.h(json.dumps(data))
        self.sock.send([data, [[pubkey, list(cg.sign(h, privkey))] for privkey, pubkey in
                               zip(self.privkeys, self.pubkeys)]])
        ############
        self.sock.listen(1)
        self.conn = Proto(self.sock.accept()[0])
        data = self.conn.recv()
        hdata = json.loads(data.decode('utf-8'))
        hdata.pop('pubkeys')
        h = cg.h(json.dumps(hdata))
        data = json.loads(data.decode('utf-8'))
        pubkeys = data['pubkeys']
        for pubkey, sign in pubkeys:
            if not cg.verify_sign(sign, h, pubkey):
                pubkeys.remove([pubkey, sign])
        if data['delta'] < 0:
            if data['delta'] >= -1000:
                bch[len(bch) - data['delta'] - 1] = block.Block.from_json(data['blocks'][1])
                for b in data['blocks'][1:]:
                    bch.append(b)
            else:
                bch[len(bch) - data['delta'] - 1] = block.Block.from_json(data['blocks'][1])
                for b in data['blocks'][1:]:
                    bch.append(b)
                get_many_blocks(data['delta'], -1000)
        lb = data['lb']
        if len(lb.txs) > len(bch[-1].txs) and lb.is_valid(bch):
            b.txs = lb.txs
        b.powminers = set(b.powminers) | set(lb.powminers)
        b.pocminers = set(b.pocminers) | set(lb.pocminers)
        if len(lb.contracts) > len(b.contracts) and lb.is_valid(bch):
            b.contracts = lb.contracts
        b.update()
        bch[-1] = b
        mymess = {}
        if mymess['delta'] > 0:
            if mymess['delta'] < 1000:
                mymess['blocks'] = [str(b) for b in bch[len(bch) + mymess['delta'] - 1:]]
            else:
                mymess['blocks'] = [str(b) for b in bch[-1000:]]
        self.conn.send(mymess)
        self.conn.close()
        return pubkeys


class InputConnection(Proto, Thread):
    """
    It is an input connection (Second user in net's doc).
    """

    def __init__(self, conn, privkey, pubkey):
        self.privkey = privkey
        self.pubkey = pubkey

        super(Proto).__init__(conn)
        super(Thread).__init__(target=self.connect)
        self.start()

    def connect(self, *_):
        data = self.recv()
        hdata = json.loads(data.decode('utf-8'))
        hdata.pop('pubkeys')
        h = cg.h(json.dumps(hdata))
        data = json.loads(data.decode('utf-8'))
        pubkeys = data['pubkeys']
        for pubkey, sign in pubkeys:
            if not cg.verify_sign(sign, h, pubkey):
                pubkeys.remove([pubkey, sign])
        sync = 'len(bch)' in data.keys()
        if sync:
            mymess = {'delta': data['len(bch)'] - len(bch)}
            if mymess['delta'] < 0:
                if mymess['delta'] > -1000:
                    mymess['blocks'] = [str(b) for b in bch[len(bch) + mymess['delta'] - 1:]]
                else:
                    mymess['blocks'] = [str(b) for b in bch[-1000:]]
            lb = block.Block.from_json(data['lb'])
            mymess['lb'] = bch[-1]
            b = bch[-1]
            if len(lb.txs) > len(bch[-1].txs) and lb.is_valid(bch):
                b.txs = lb.txs
            b.powminers = set(b.powminers) | set(lb.powminers)
            b.pocminers = set(b.pocminers) | set(lb.pocminers)
            if len(lb.contracts) > len(b.contracts) and lb.is_valid(bch):
                b.contracts = lb.contracts
            bch[-1] = b
            mymess['lb'] = bch[-1]
        mymess['answer'] = handle_request(data['request'])
        self.send(mymess)
        if sync:
            if mymess['delta'] > 0:
                data = self.recv()
                data = json.loads(data.decode('utf-8'))
                if data['delta'] < 0:
                    if data['delta'] >= -1000:
                        bch[len(bch) - data['delta'] - 1] = block.Block.from_json(data['blocks'][1])
                        for b in data['blocks'][1:]:
                            bch.append(b)
        self.close()
        return pubkeys

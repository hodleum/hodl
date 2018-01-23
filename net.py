import block
import socket
import multiprocessing
import json


class Peers(set):
    def clear_not_valid_peers(self):
        for peer in self:
            if not True:
                self.remove(peer)

    def save(self, file):
        with open(file, 'w') as f:
            f.write(json.dumps([json.dumps(peer) for peer in list(self)]))

    def open(self, file):
        with open(file, 'r') as f:
            for peer in json.loads(f.read()):
                self.add(json.loads(peer))


class Connection:
    def __init__(self, ip):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        data = {'len(bch)':len(bch), 'lb':str(bch[-1])}
        self.sock.send(json.dumps(data).encode('utf-8'))
        self.sock.bind((ip, port))[0]
        self.sock.listen(1)
        self.conn = self.sock.accept()[0]
        data = b''
        while True:
            data += self.conn.recv(1024)
            if not data:
                break
        data = json.loads(data.decode('utf-8'))
        if data['delta'] < 0:
            if data['delta'] >= -1000:
                bch[len(bch)-data['delta'] - 1] = block.block_from_json(data['blocks'][1])
                for b in data['blocks'][1:]:
                    bch.append(b)
        lb = data['lb']
        if len(lb.txs) > len(bch[-1].txs) and lb.is_valid(bch):
            b.txs = lb.txs
        b.powminers = set(b.powminers) | set(lb.powminers)
        b.pocminers = set(b.pocminers) | set(lb.pocminers)
        if len(lb.contracts) > len(b.contracts) and lb.is_valid(bch):
            b.contracts = lb.contracts
        bch[-1] = b
        mymess = {}
        if mymess['delta']>0:
            if mymess['delta']<1000:
                mymess['blocks'] = [str(b) for b in bch[len(bch)+mymess['delta']-1:]]
            else:
                mymess['blocks'] = [str(b) for b in bch[-1000:]]
        self.conn.send(json.dumps(mymess).encode('utf-8'))



class InputConnection:
    def __init__(self, conn):
        self.conn = conn
        self.proc = multiprocessing.Process(target=self.connect)
        self.proc.start()
        self.proc.join()

    def connect(self):
        data = b''
        while True:
            data += self.conn.recv(1024)
            if not data:
                break
        data = json.loads(data.decode('utf-8'))
        mymess = {'delta':data['len(bch)']-len(bch)}
        if mymess['delta']<0:
            if mymess['delta']>-1000:
                mymess['blocks'] = [str(b) for b in bch[len(bch)+mymess['delta']-1:]]
            else:
                mymess['blocks'] = [str(b) for b in bch[-1000:]]
        lb = block.block_from_json(data['lb'])
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
        self.conn.send(json.dumps(mymess).encode('utf-8'))
        if mymess['delta']>0:
            self.conn = self.sock.accept()[0]
            data = b''
            while True:
                data += self.conn.recv(1024)
                if not data:
                    break
            data = json.loads(data.decode('utf-8'))
            if data['delta'] < 0:
                if data['delta'] >= -1000:
                    bch[len(bch) - data['delta'] - 1] = block.block_from_json(data['blocks'][1])
                    for b in data['blocks'][1:]:
                        bch.append(b)


global bch
bch = block.Blockchain()
global peers
peers = Peers()
port = 6666

def get_many_blocks(minb, maxb):
    pass

def handle_request(req):
    pass

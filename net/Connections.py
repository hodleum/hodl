import json
import socket
import multiprocessing
import block


global bch
bch = block.Blockchain()


def get_many_blocks(minb, maxb):
    blocks = []
    return blocks


def handle_request(req):
    ans = []
    return ans


def get_smart_contracts_mem(ind, start=0, stop=-1):
    pass


class ConnectionErr(Exception):
    pass


class Connection:
    """
    It is an output connection (First user in net's doc).
    """
    def __init__(self, ip, port):
        self.proc = multiprocessing.Process(target=self.connect, args=(ip, port))
        self.proc.start()
        self.proc.join()

    def connect(self, ip, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, port))
            data = {'len(bch)': len(bch), 'lb': str(bch[-1])}
            self.sock.send(json.dumps(data).encode('utf-8'))
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
                    bch[len(bch)-data['delta'] - 1] = block.Block.from_json(data['blocks'][1])
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
                    mymess['blocks'] = [str(b) for b in bch[len(bch)+mymess['delta']-1:]]
                else:
                    mymess['blocks'] = [str(b) for b in bch[-1000:]]
            self.conn.send(json.dumps(mymess).encode('utf-8'))
        except:
            return ConnectionErr()


class InputConnection:
    """
    It is an input connection (Second user in net's doc).
    """
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
        lb = block.Block.Block.from_json(data['lb'])
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
        if mymess['delta'] > 0:
            data = b''
            while True:
                data += self.conn.recv(1024)
                if not data:
                    break
            data = json.loads(data.decode('utf-8'))
            if data['delta'] < 0:
                if data['delta'] >= -1000:
                    bch[len(bch) - data['delta'] - 1] = block.Block.from_json(data['blocks'][1])
                    for b in data['blocks'][1:]:
                        bch.append(b)

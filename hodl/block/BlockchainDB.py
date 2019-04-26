from .Block import Block, get_prevhash
import sqlite3
from threading import RLock
import logging as log


# genesis block
with open('tests/genblock.bl', 'r') as f:
    genblock = Block.from_json(f.readline())
lock = RLock()


class BlockchainDB:
    """
    Blockchain database
    """
    def __init__(self, filename='bch.db', m='w'):
        """
        Init
        :param filename: filename for database
        :type filename: str
        :param m: mode
        :type m: str
        """
        if m != 'ro':
            self.conn = sqlite3.connect('db/' + filename, check_same_thread=False)
        else:
            self.conn = sqlite3.connect('db/' + filename + '?mode=ro', uri=True, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS blocks
                     (ind integer primary key , block text)''')
        try:
            self[0]
        except:
            self[0] = genblock
        self.conn.commit()

    def __len__(self):
        lock.acquire(True)
        self.cursor.execute("SELECT COUNT(*) FROM blocks")
        l = int(self.cursor.fetchone()[0])
        lock.release()
        return l

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, item):
        if type(item) == slice:
            blocks = []
            if item.step is None:
                step = 1
            else:
                step = item.step
            for i in range([item.start, len(self)][item.stop is not None], [item.stop, len(self)][item.stop is None],
                           [step, len(self)][item.stop is not None]):
                blocks.append(self[i])
            return blocks
        elif type(item) == tuple:
            tnx = self[item[0]].txs[item[1]]
            if tnx.sc:
                return tnx.sc
            else:
                return tnx
        elif item < 0:
            item += len(self)
        lock.acquire(True)
        self.cursor.execute("SELECT block FROM blocks WHERE ind=?", (item,))
        try:
            s = self.cursor.fetchone()[0]
        except TypeError:
            raise IndexError(f'block {item} does not exists')
        lock.release()
        return Block.from_json(s)

    def __setitem__(self, key, value):
        lock.acquire(True)
        if key < 0:
            key += len(self)
        if type(key) == tuple:
            b = self[key[0]]
            b.txs[key[1]] = value
            self[key[0]] = b
            return
        self.cursor.execute("UPDATE blocks SET block=? WHERE ind=?", (str(value), key))
        self.conn.commit()
        lock.release()

    def append(self, block):
        """
        Appends blockchain with a block
        :param block: block to add in blockchain
        :type block: Block
        """
        log.debug(f'appending blockchain with block, len(self): {len(self)}')
        lock.acquire(True)
        if len(self):
            block.prevhash = get_prevhash(self)
        self.cursor.execute("INSERT INTO blocks VALUES (?, ?)", (len(self), str(block)))
        self.conn.commit()
        lock.release()
        log.debug(f'appended blockchain with block, len(self): {len(self)}')

    def index(self, block):
        """
        Finds block in chain (by hash)
        :param block: block to index
        :type block: Block
        :return: index
        :rtype: int
        """
        for i in range(len(self)):
            if self[i].h == block.h:
                return i

    def clear(self):
        """
        Delete all blocks from blockchain
        """
        lock.acquire(True)
        self.cursor.execute('''DELETE FROM blocks WHERE 1=1''')
        self.conn.commit()
        lock.release()

    def commit(self):
        self.close()
        self.conn = sqlite3.connect(self.f)
        self.cursor = self.conn.cursor()

    def close(self):
        """Close connection to database"""
        self.conn.commit()
        self.conn.close()

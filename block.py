import cryptogr as cg
import time


class Blockchain:    # класс для цепочки блоков
    def __init__(self):
        self.blocks=[]


class Block:     # класс для блоков
    def __init__(self, ind, previousHash, txs, creator):
        self.i = ind
        self.prevhash = previousHash
        self.timestamp = time.time()
        self.txs = txs
        self.creator = creator
        self.update()

    def append(self, txn):    # функция для добавления транзакции в блок
        self.txs.append(txn)
        self.update()

    def update(self):
        h = str(self.i) + str(self.prevhash) + str(self.timestamp)
        for t in self.txs:
            h = h + str(t.hash)
        self.head = cg.h(str(h))

    def isValid(self, previndex):    # проверка валидности каждой транзакции блока и соответствия хэша
        h = str(self.i) + str(self.prevhash) + str(self.timestamp)
        for t in self.txs:
            h = h + str(t.hash)

        v = cg.h(str(h)) == self.head and self.i == previndex + 1
        return v


class Transaction(dict):
    def __init__(self, author, froms, outs, outns, sign='signing'):
        self['froms'] = froms  # numbers of transactions([number of block, number of needed tnx in this block]), from which this transaction takes money
        self['outs'] = outs  # numbers of wallets, to which is this tnx
        self['outns'] = outns  # how much money to each of outs
        self['time'] = time.time()
        self['author'] = author
        if sign=='signing':
            self['sign'] = cg.sign(str(self['froms']) + str(self['outs']) + str(self['outns']) + str(self['time']))
        else:
            self['sign'] = sign
        x = ''
        x = x + str(self['sign'])
        x = x + str(self['author'])
        x = x + str(self['time'])
        for f in self['froms']:
            x = x + str(f)
        for f in self['outs']:
            x = x + str(f)
        for f in self['outns']:
            x = x + str(f)
        self.hash = cg.h(str(x))

    def isvalid(self, bch):    # проверка наличия требуемых денег в транзакциях, из которых берутся деньги и соответствия хэша
        if not cg.verify_sign(self['sign'], str(self['froms']) + str(self['outs']) + str(self['outns']) + str(self['time']), self['author']):
            return False
        inp=0
        for t in self['froms']:
            try:
                txs = bch.blocks[t[0]].txs[t[1]]
                if not txs.isvalid:
                    return False
                inp = inp + txs['outns'][txs['outs'].index(self['author'])]
            except:
                return False
        o = 0
        for n in self['outns']:
            o = o + n
        if not o == inp:
            return False
        x = ''
        x = x + str(self['sign'])
        x = x + str(self['author'])
        x = x + str(self['time'])
        for f in self['froms']:
            x = x + str(f)
        for f in self['outs']:
            x = x + str(f)
        for f in self['outns']:
            x = x + str(f)
        if not self.hash == cg.h(str(x)):
            return False
        return True

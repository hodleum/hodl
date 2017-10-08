import cryptogr as cg
import time


class Blockchain:    # класс для цепочки блоков
    def __init__(self):
        self.blocks=[]
    def append(self, block):    # добавить новый блок
        self.blocks.append(block)
    def money(self, wallet):    # проверяет, сколько денег у wallet
        money = 0
        for block in self.blocks:
            for txs in block.txs:
                if wallet in txs['outs']:
                    money += txs['outns'][txs['outs'].index(wallet)]
        return money

    def newblock(self, n, creator, txs=[]):
        self.append(Block(n, creator, self, txs))


class Block:     # класс для блоков
    def __init__(self, n, creator, bch, txs=[]):
        self.n = n
        self.prevhash = bch.blocks[-1].h
        self.timestamp = time.time()
        self.txs = txs
        self.creator = creator
        self.update(bch)

    def append(self, txn, bch):    # функция для добавления транзакции в блок
        self.txs.append(txn)
        self.update(bch)

    def update(self, bch):    # обновляет хэш
        h = str(bch.blocks.index(self)) + str(self.prevhash) + str(self.timestamp) + str(self.n)
        for t in self.txs:
            h = h + str(t.hash)
        self.h = cg.h(str(h))

    def isValid(self, bch):    # проверка валидности каждой транзакции блока и соответствия хэша
        h = str(bch.blocks.index(self)) + str(self.prevhash) + str(self.timestamp) + str(self.n)
        for t in self.txs:
            h = h + str(t.hash)
        v = cg.h(str(h)) == self.h and self.prevhash == bch.blocks[bch.blocks.index(self)-1].h
        return v


class Transaction(dict):
    # форма для передачи транзакций строкой: txs['author']+'а'(русское а)+';'.join(self['froms'])+'а'+';'.join(self['outs']+'а'+';'.join(self['outns'])+'а'+str(self['time'])+'а'+str(self['sign']))
    def tostr(self):    # преобразование в строку, которая может быть расшифрована функцией fromstr
        return self['author'] + 'а'+str(self['froms']) + 'а' + str(self['outs']) + 'а' + str(self['outns']) + 'а' + str(self['time']) + 'а' + str(self['sign'])

    def fromstr(self, str):
        l=str.split('а')
        self.gen(l[0], eval(l[1]), eval(l[2]), eval(l[3]), l[5], float(l[4]))


    def gen(self, author, froms, outs, outns, sign='signing', privkey='me', timestamp='signing'):
        self['froms'] = froms  # numbers of transactions([number of block, number of needed tnx in this block]), from which this transaction takes money
        self['outs'] = outs  # numbers of wallets, to which is this tnx
        self['outns'] = outns  # how much money to each of outs
        self['author'] = author  # тот, кто проводит транзакцию
        if sign=='signing':    # транзакция может быть уже подписана, или может создаваться новая транзакция с помощью Transaction(). Соответственно может быть новая подпись.
            if privkey=='me':
                self['sign'] = cg.sign(str(self['froms']) + str(self['outs']) + str(self['outns']) + str(self['time']))
            else:
                self['sign'] = cg.sign(str(self['froms']) + str(self['outs']) + str(self['outns']) + str(self['time']), privkey)
            self['time'] = time.time()
        else:
            self['sign'] = sign
            self['time'] = timestamp
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

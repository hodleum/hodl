import cryptogr as cg
import time


minerfee = 1
txs_in_block = 50
maxblocksize = 40000
# todo: ТЕСТЫ! ОЧЕНЬ НАДО ПОТЕСТИТЬ! (для этого надо НАКОНЕЦ ДОПИСАТЬ cryptogr.py) Файл практически не тестился.

class Blockchain:    # класс для цепочки блоков
    def __init__(self):
        self.blocks = []

    def append(self, block):    # добавить новый блок
        self.blocks.append(block)

    def money(self, wallet):    # проверяет, сколько денег у wallet
        money = 0
        for block in self.blocks:   # перебираем все транзакции в каждом блоке
            for txs in block.txs:
                if wallet in txs.outs and txs.is_open(self):
                    money += txs.outns[txs.outs.index(wallet)]
        return money

    def new_block(self, n, creator, txs=[]):   # создает новый блок и сразу же добавляет его в цепочку.
        self.append(Block(n, creator, self, txs))

    def is_valid(self):
        for b in self.blocks:
            if not b.is_valid(self):
                return False
        return True

    def new_transaction(self, author, froms, outs, outns, sign = 'signing', privkey = 'me'):
        tnx = Transaction()
        for block in self.blocks:
            if not block.is_full():
                tnx.gen(author, froms, outs, outns, (self.blocks.index(block), len(block.txs)), sign, privkey)
                block.append(tnx, self)
                break

    def tostr(self):
        s = ''
        for block in self.blocks:
            s += 'д' + block.tostr()

    def fromstr(self, s):
        self.blocks = []
        s = s.split('д')
        for b in s:
            block = Block()
            block.fromstr(b)
            self.append(block)


class Block:     # класс для блоков
    def __init__(self, n = 0, creator = '', bch = Blockchain(), txs=[], contracts=[]):
        self.n = n
        try:
            self.prevhash = bch.blocks[-1].h
        except:
            self.prevhash = 0
        self.timestamp = time.time()
        tnx0 = Transaction()
        tnx0.gen('mining', [['nothing']], [creator], [minerfee], [len(bch.blocks), 0], 'mining', 'mining')
        self.txs = [tnx0] + txs
        self.contracts = contracts
        self.creator = creator
        self.update(bch)

    def tostr(self):
        s = ''
        for t in self.txs:
            s += t.tostr() + 'б'
        s += 'г' + str(self.n) + 'б' + str(self.timestamp) + 'б' + str(self.prevhash) + 'б' + str(self.creator)
        s += 'г'
        for c in self.contracts:
            s += c.tostr + 'б'
        return s
    def fromstr(self, s):
        s = s.split('г')
        txs = s[0].split('б')
        self.txs = []
        for t in txs:
            tnx = Transaction()
            tnx.fromstr(t)
            self.txs.append(tnx)
        scs = s[2].split('б')
        self.contracts = []
        for sc in scs:
            contract = Smart_contract()
            contract.fromstr(sc)
            self.contracts.append(contract)
        pars = s[1].split('б')
        self.n, self.timestamp, self.prevhash, self.creator = pars[0], pars[1], pars[2], pars[3]

    def append(self, txn, bch):    # функция для добавления транзакции в блок
        self.txs.append(txn)    # добавляем транзакцию в список транзакций
        self.update(bch)    # обновляем хэш

    def update(self, bch):    # обновляет хэш
        h = str(len(bch.blocks)) + str(self.prevhash) + str(self.timestamp) + str(self.n)
        for t in self.txs:
            h = h + str(t.hash)
        self.h = cg.h(str(h))

    def is_valid(self, bch):    # проверка валидности каждой транзакции блока и соответствия хэша
        h = str(bch.blocks.index(self)) + str(self.prevhash) + str(self.timestamp) + str(self.n)
        if self.txs[0].froms != [['nothing']] or self.txs[0].author != 'mining' \
                or self.txs[0].outs != [self.creator]\
                or self.txs[0].outns != minerfee:
            return False
        for t in self.txs[1:]:
            h = h + str(t.hash)
            if not t.is_valid():
                return False
        v = cg.h(str(h)) == self.h and self.prevhash == bch.blocks[bch.blocks.index(self)-1].h
        return v

    def is_full(self):
        return self.tostr >= maxblocksize


class Transaction:
    # форма для передачи транзакций строкой(разделитель - русское а):
    # author + а + str(froms)+ а + str(outs) + а + str(outns) + а + str(time)+ а + sign
    def tostr(self):    # преобразование в строку, которая может быть расшифрована функцией fromstr
        return self.author + 'а'+str(self.froms) + 'а' + str(self.outs) + 'а' + str(self.outns) + 'а' \
                + 'а' + str(self.sign)

    def fromstr(self, s):   # Обратная функция tostr
        l = s.split('а')
        self.gen(l[0], eval(l[1]), eval(l[2]), eval(l[3]), l[5])

    def gen(self, author, froms, outs, outns, index, sign = 'signing', privkey = 'me'):
        self.froms = froms  # номера транзакций([номер блока в котором лежит нужная транзакция,
                               # номер нужной транзакции в блоке),
                               # из которых эта берет деньги
        self.outs = outs    # номера кошельков-адресатов
        self.outns = outns  # количество денег на каждый кошелек-адресат
        self.author = author  # тот, кто проводит транзакцию
        self.index = index
        if sign == 'signing':    # транзакция может быть уже подписана,
                               # или может создаваться новая транзакция с помощью Transaction().
                               # Соответственно может быть нужна новая подпись.
            if privkey == 'me':     # Подписываем транзакцию тем ключом, который сохранен на этом компьютере как основной
                self.sign = cg.sign(str(self.froms) + str(self.outs) + str(self.outns))
            else:    # Или кастомным
                self.sign = cg.sign(str(self.froms) + str(self.outs) + str(self.outns),
                                       privkey)
        else:    # Если транзакция не проводится, а создается заново после передачи, то подпись уже известна
            self.sign = sign
        x = ''    # считаем хэш
        x = x + str(self.sign)
        x = x + str(self.author)
        for f in self.froms:
            x = x + str(f)
        for f in self.outs:
            x = x + str(f)
        for f in self.outns:
            x = x + str(f)
        x += str(index)
        self.hash = cg.h(str(x))

    def is_valid(self, bch):    # Проверка наличия требуемых денег
                                # в транзакциях, из которых берутся деньги и соответствия подписи и хэша
                                # todo: сделать, чтобы транзакция, совершенная смарт-контрактом, обрабатывалась отдельно
                                # Проверка соответствия подписи
        if not cg.verify_sign(self.sign, str(self.froms) + str(self.outs)
                + str(self.outns), self.author):
            return False
        inp = 0
        for t in self.froms:    # Проверка наличия требуемых денег в транзакциях-донорах
            try:
                txs = bch.blocks[t[0]].txs[t[1]]
                if not txs.is_valid:
                    return False
                if not txs.is_open():
                    return False
                inp = inp + txs.outns[txs.outs.index(self.author)]
            except:
                return False    # Если возникает какая-нибудь ошибка, то транзакция точно невалидная
        o = 0
        for n in self.outns:  # должны быть израсходованы все взятые деньги
            o = o + n
        if not o == inp:
            return False
        x = ''  # проверка соответствия хэша
        x = x + str(self.sign)
        x = x + str(self.author)
        for f in self.froms:
            x = x + str(f)
        for f in self.outs:
            x = x + str(f)
        for f in self.outns:
            x = x + str(f)
        if not self.hash == cg.h(str(x)):
            return False
        return True

    def is_open(self, bch):  # Проверяет, не является ли эта транзакция чьим-то донором
        for block in bch.blocks:   # перебираем все транзакции в каждом блоке
            for txs in block.txs:
                if self.index in txs.froms:
                    return False
        return True

class Smart_contract:
    # todo: дописать Smart_contract: добавить виды контрактов, входную информацию, ограничения
    def __init__(self, text, author, index, payment_method = 'for execution', payment_opts={'for 1 execution' : 1}):
        self.text = text
        self.author = author
        self.payment_method = payment_method
        self.index = index
        self.result = ''

    def execute(self, addr, bch):
        froms = []
        outs = []
        outns = []
        result = ''
        import kcvm
        exec(self.text)    # Смарт-контракт изменяет переменные froms, outs и outns на параметры совершаемой
        # им транзакции. Если ему не надо совершать транзакцию, он их не изменяет. Также он может возвращать result.
        # класс result - str
        try:
            bch.new_transaction('sc' + self.index[0] + ';' + self.index[1], froms, outs, outns,
                                'sc' + self.index[0] + ';' + self.index[1],
                                'sc' + self.index[0] + ';' + self.index[1])
        except:
            pass
        self.result = result

    def tostr(self):
        pass    # todo: дописать Smart_contract.tostr() и Smart_contract.fromstr()

    def fromstr(self, s):
        pass

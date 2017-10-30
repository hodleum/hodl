import cryptogr as cg
import time
from itertools import chain


minerfee = 1
txs_in_block = 50
maxblocksize = 40000
# todo: ТЕСТЫ! ОЧЕНЬ НАДО ПОТЕСТИТЬ! (для этого надо НАКОНЕЦ ДОПИСАТЬ cryptogr.py) Файл практически не тестился.
class Blockchain(list):
    """класс для цепочки блоков"""
    def money(self, wallet):    # проверяет, сколько денег у wallet
        money = 0
        for block in self:   # перебираем все транзакции в каждом блоке
            for txs in block.txs:
                if wallet in txs.outs and txs.is_open(self):
                    money += txs.outns[txs.outs.index(wallet)]
        return money

    def new_block(self, n, creator, txs=[]):
        """создает новый блок и сразу же добавляет его в цепочку."""
        self.append(Block(n, creator, self, txs))

    def is_valid(self):
        """проверяет валидность всей цепочки"""
        for b in self:
            if not b.is_valid(self):
                return False
        return True

    def new_transaction(self, author, froms, outs, outns, sign='signing', privkey=''):
        tnx = Transaction()
        for i, block in enumerate(self[1:]):
            if not block.is_full():
                tnx.gen(author, froms, outs, outns, (i, len(block.txs)), sign, privkey)
                block.append(tnx, self)
                break

    def __str__(self):
        s = ''
        for block in self:
            s += 'д' + str(block)
        return s

    def fromstr(self, s):
        self = []
        s = s.split('д')
        for b in s:
            block = Block()
            block.fromstr(b)
            self.append(block)

    def new_sc(self, text, author, needsinf=False, payment_method='for execution', payment_opts={'for 1 execution': 1}):
        for i, block in enumerate(self):
            if not block.is_full():
                block.contracts.append(text, author, (i, len(block.contracts)), needsinf, payment_method, payment_opts)
                break


class Block:     # класс для блоков
    def __init__(self, n=0, creator='', bch=Blockchain(), txs=[], contracts=[]):
        self.n = n
        try:
            self.prevhash = bch[-1].h
        except:
            self.prevhash = '0'
        self.timestamp = time.time()
        tnx0 = Transaction()
        tnx0.gen('mining', [['nothing']], [creator], [minerfee], (len(bch), 0), 'mining', 'mining')
        self.txs = [tnx0] + txs
        self.contracts = contracts
        self.creator = creator
        self.update()

    def __str__(self):
        s = ''
        for t in self.txs:
            s += str(t) + 'б'
        s = s[:-1]
        s += 'г' + str(self.n) + 'б' + str(self.timestamp) + 'б' + str(self.prevhash) + 'б' + str(self.creator)
        s += 'г'
        for c in self.contracts:
            s += str(c) + 'б'
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
        for sc in scs[:-1]:
            contract = Smart_contract('', '', [0,0])
            contract.fromstr(sc)
            self.contracts.append(contract)
        pars = s[1].split('б')
        self.n, self.timestamp, self.prevhash, self.creator = int(pars[0]), float(pars[1]), str(pars[2]), str(pars[3])
        self.update()

    def append(self, txn, bch):    # функция для добавления транзакции в блок
        self.txs.append(txn)    # добавляем транзакцию в список транзакций
        self.update()    # обновляем хэш

    def update(self):    # обновляет хэш
        h = ''.join([str(self.prevhash), str(self.timestamp), str(self.n)]+[str(t.hash) for t in self.txs])
        self.h = cg.h(str(h))

    def is_valid(self, bch):    # проверка валидности каждой транзакции блока и соответствия хэша
        h = str(bch.index(self)) + str(self.prevhash) + str(self.timestamp) + str(self.n)
        if self.txs[0].froms != [['nothing']] or self.txs[0].author != 'mining' \
                or self.txs[0].outs != [self.creator]\
                or self.txs[0].outns != minerfee:
            return False
        for t in self.txs[1:]:
            h = h + str(t.hash)
            if not t.is_valid(bch):
                return False
        v = cg.h(str(h)) == self.h and self.prevhash == bch[bch.index(self)-1].h
        return v

    def is_full(self):
        return len(str(self)) >= maxblocksize


class Transaction:
    # форма для передачи транзакций строкой(разделитель - русское а):
    # author + а + str(froms)+ а + str(outs) + а + str(outns) + а + str(time)+ а + sign
    def __str__(self):    # преобразование в строку, которая может быть расшифрована функцией fromstr
        return self.author + 'а'+str(self.froms) + 'а' + str(self.outs) + 'а' + str(self.outns) + 'а' \
                + str(self.index) \
                + 'а' + str(self.sign)
    # todo: заменить fromstr на from_json
    def fromstr(self, s):   # Обратная функция tostr
        l = s.split('а')
        self.gen(l[0], eval(l[1]), eval(l[2]), eval(l[3]), eval(l[4]), l[5])

    def gen(self, author, froms, outs, outns, index, sign='signing', privkey=''):
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
            self.sign = cg.sign(str(self.froms) + str(self.outs) + str(self.outns), privkey)
        else:    # Если транзакция не проводится, а создается заново после передачи, то подпись уже известна
            self.sign = sign
        x = ''.join(chain([str(self.sign), str(self.author), str(self.index)], [str(f) for f in self.froms],
                          [str(f) for f in self.outs], [str(f) for f in self.outns]))
        self.hash = cg.h(str(x))

    def is_valid(self, bch):    # Проверка наличия требуемых денег
                                # в транзакциях, из которых берутся деньги и соответствия подписи и хэша
                                # Проверка соответствия подписи
        if not self.author[0:2] == 'sc':
            if not cg.verify_sign(self.sign, str(self.froms) + str(self.outs) + str(self.outns), self.author):
                print(self.index, 'is not valid: sign is wrong')
                return False
        else:
            try:
                scind = [int(self.author[2:].split(';')[0]), int(self.author[2:].split(';')[1])]
                sc = bch[scind[0]].contracts[scind[1]]
                tnx_needed, tnx_created, froms, outs, outns = sc.exec()[1:]
                if tnx_needed:
                    selfind = froms.index(self.froms)
                    if not (tnx_created and outs[selfind] == self.outs and outns[selfind]==self.outns):
                        return False
                else:
                    print(self.index, 'is not valid: sc')
                    return False
            except:
                print(self.index, 'is not valid: exception183')
                return False
        inp = 0
        for t in self.froms:    # Проверка наличия требуемых денег в транзакциях-донорах
            try:
                if t == ['nothing']:
                    if not (self.index[1] == 0 and self.outs[0] == bch[self.index[0]].creator):
                        return False
                    inp = minerfee
                else:
                    txs = bch[int(t[0])].txs[int(t[1])]
                    if not txs.is_valid:
                        print(self.index, 'is not valid: from is not valid')
                        return False
                    if not txs.is_open():
                        print(self.index, 'is not valid: from is not valid')
                        return False
                    inp = inp + txs.outns[txs.outs.index(self.author)]
            except:
                print(self.index, 'is not valid: exception197')
                return False    # Если возникает какая-нибудь ошибка, то транзакция точно невалидная
        o = 0
        for n in self.outns:  # должны быть израсходованы все взятые деньги
            o = o + n
        if not o == inp:
            print(self.index, 'is not valid: not all money')
            return False
        x = ''.join(chain([str(self.sign), str(self.author), str(self.index)], [str(f) for f in self.froms],
                        [str(f) for f in self.outs], [str(f) for f in self.outns]))
        if not self.hash == cg.h(str(x)):
            print(self.index, 'is not valid: hash is not valid')
            return False
        return True

    def is_open(self, bch):  # Проверяет, не является ли эта транзакция чьим-то донором
        for block in bch:   # перебираем все транзакции в каждом блоке
            for txs in block.txs:
                if self.index in txs.froms:
                    return False
        return True

class Smart_contract:
    # todo: дописать Smart_contract: добавить ограничения
    def __init__(self, text, author, index, needsinf=False, payment_method = 'for execution', payment_opts={'for 1 execution' : 1}):
        self.text = text
        self.author = author
        self.payment_method = payment_method
        self.index = index
        self.result = ''
        self.needsinf = needsinf
        self.payment_opts = payment_opts

    def execute(self, bch, inf=''):
        loc = {}
        if self.needsinf:
            exec(self.text, {'inf': str(inf)}, loc)
        else:
            exec(self.text, {}, loc)
        result = loc['result']
        tnx_needed = loc['tnx_needed']    # смарт-контракт может проводить транзакции от своего имени
        tnx_created = loc['tnx_created']
        froms = loc['froms']
        outs = loc['outs']
        outns = loc['outns']
        sc_needed = loc['sc_needed']    # смарт-контракт может создавать смарт-контракты
        sc_created = loc['sc_created']
        sc_text = loc['sc_text']
        sc_author = loc['sc_author']
        sc_payment_method = loc['sc_payment_method']
        sc_needsinf = loc['sc_needsinf']
        sc_payment_opts = loc['sc_payment_opts']
        # Смарт-контракт изменяет переменные froms, outs и outns на параметры совершаемой
        # им транзакции. Если ему не надо совершать транзакцию, он их не изменяет. Также он может возвращать result.
        # класс result - str
        if not self.needsinf:   # контракты, которые принимают входную информацию не могут создавать другие контракты и транзакции
            if tnx_needed:
                for i in range(len(froms)):
                    if not tnx_created[i]:
                        try:
                            bch.new_transaction('sc' + str(self.index[0]) + ';' + str(self.index[1]), froms[i], outs[i], outns[i],
                                                'sc' + str(self.index[0]) + ';' + str(self.index[1]),
                                                'sc' + str(self.index[0]) + ';' + str(self.index[1]))
                        except:
                            pass
            if sc_needed:
                for i in range(len(sc_created)):
                    if not sc_created[i]:
                        try:
                            bch.new_sc(sc_text[i], sc_author[i], sc_needsinf[i], sc_payment_method[i], sc_payment_opts[i])
                        except:
                            pass
        self.result = result
        return result, tnx_needed, tnx_created, froms, outs, outns

    def __str__(self):
        return str(self.text) + 'е' + str(self.author) + 'е' + str(self.index[0]) + ';' + str(self.index[1]) + 'e' + \
             str(self.needsinf) + 'е' + str(self.payment_method) + 'е' + str(self.payment_opts)

    # from_json
    @classmethod
    def fromstr(cls, s):
        # получить данные из строки
        s = s.split('е')
        text = s[0]
        author = s[1]
        index = [int(s[2].split(';')[0]), int(s[2].split(';')[1])]
        needsinf = eval(s[3])
        payment_method = s[4]
        payment_opts = eval(s[5])
        # собрать новый объект
        return cls(text, author, index, needsinf, payment_method, payment_opts)

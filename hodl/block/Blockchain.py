"""
Classes:
Blockchain:
Class for storing blockchain. Connects to the sqlite3 database
Main methods:
    new_block - creates new block
    new_transaction - creates new transaction
    new_sc - creates new smart contract
Block:
Class for storing block
Transaction:
Class for storing transaction.
Smart_contract:
Class for storing smart contract.
Some abbreviations:
bch - blockchain
tnx - transaction
sc - smart contract(DApp)
"""
from .sc import *
from .Transaction import *
from .BlockchainDB import BlockchainDB, genblock
import re


# todo: blockchain freeze before new block or other consensus mechanism
# todo: transaction and smart contract limit or hash mining, remove smart contract's comission
# todo: SC messages connected to transaction
# todo: make available bch[i].attr = value and bch[i].attr1.attr2 = value using __setattr__
# todo: remove transaction froms
# todo: remove nicks
# todo: Block and UnfilledBlock as one class


class Blockchain(BlockchainDB):
    """Class for blockchain"""
    def tnxiter(self, maxn=None, fr=(0, 0)):
        """
        Iterate in all transactions in blockchain
        :param maxn: maximum tnx index (latest tnx of all transactions to iterate in)
        :param fr: minimum tnx index (earliest tnx of all transactions to iterate in)
        """
        if maxn is None:
            maxn = ['l', 'l']
        maxn = list(maxn)
        if maxn[0] == 'l':
            maxn[0] = len(self)
        if maxn[1] == 'l':
            maxn[1] = len(self[-1].txs)
        if maxn[0] < 0:
            maxn[0] = len(self) + maxn[0]
        if maxn[1] < 0:
            maxn[1] = len(self[-1].txs) + maxn[1]
        if fr[0] > maxn[0]:
            return
        else:
            for i in range(fr[0], maxn[0]):
                for j in range(len(self[i].txs)):
                    if i == fr[0] and j < fr[1]:
                        continue
                    if i == maxn and j >= maxn[1]:
                        break
                    yield self[i].txs[j]

    def get_sc(self, smartcontract):
        """
        Get smart contract by index
        :param smartcontract: index
        :type smartcontract: str
        :return: Smart contract
        :type: SmartContrct
        """
        smartcontract = re.sub(r'[\[\] ]', '', smartcontract).split(',')
        smartcontract = list(map(int, smartcontract))
        return self[smartcontract[0]].contracts[smartcontract[1]]

    def verify_sc_sign(self, smartcontract, sign):
        """
        Verify smart contract's sign
        :param smartcontract: smart contract's index
        :type smartcontract: str
        :param sign: sign
        :type sign: str
        :return: validness
        :type: bool
        """
        return self.get_sc(smartcontract).validate_sign(sign)

    def money(self, wallet, at=None):
        """
        Count balance of wallet
        :param wallet: wallet to count balance at
        :type wallet: str
        :param at: latest tnx to count
        :type at: list
        :return: balance
        :rtype: float
        """
        if at is None:
            at = ['l', 'l']
        money = 0
        for tnx in self.tnxiter(maxn=at):  # every tnx in every block
            outs, outns = rm_dubl_from_outs(tnx.outs, tnx.outns)
            l = zip([self.pubkey_by_nick(o) for o in outs], outns, range(len(outns)))
            for w, n, j in l:
                if (w == wallet or w == self.pubkey_by_nick(wallet)) and not tnx.spent(self)[j] \
                        and 'mining' not in tnx.outs:
                    money += n
        return round(money, 10)

    def new_transaction(self, author, froms, outs, outns, sign='signing', privkey='', sc=tuple()):
        """
        Creates new transaction and adds it to the chain
        :param str author: transaction author
        :param list froms: transaction froms
        :param list outs: transaction outs
        :param list outns: transaction outns
        :param str sign: transaction sign if it's already signed or 'signing'
        :param str privkey: private key if tnx is not already signed
        :param sc: index of smart contract connected with transaction or ()/[]/None
        :type sc: tuple or list
        :return: index of created transaction
        :rtype: list
        """
        tnx = Transaction()
        tnx.gen(author, froms, outs, outns, (len(self) - 1, len(self[-1].txs)), sign, privkey, sc=sc)
        b = self[-1]
        b.append(tnx)
        self[-1] = b
        ind = [len(self) - 1, len(self[-1].txs) - 1]
        log.info(f'created transaction with index {ind}')
        return ind

    def new_sc(self, text, author, author_priv, memsize=10000000, lang="js"):
        """
        Creates new smart contract and adds it to the chain
        :param str text: smart contract code
        :param str author: SC's author
        :param str author_priv: author's private key
        :param int memsize: SC's memory size
        :param str lang: SC language
        :return: [index of created sc, index of transaction this SC is connected with]
        :rtype: [list[int], list[int]]
        """
        log.debug('Blockchain.new_sc')
        b = self[-1]
        sc = SmartContract(text, author, [len(self) - 1, len(b.contracts)], memsize=memsize, langr=lang)
        sc.sign_sc(author_priv)
        b.contracts.append(sc)
        self[-1] = b
        sc.update(self)
        ind = len(self) - 1, len(self[-1].contracts) - 1
        tnxind = self.new_transaction(author, [], [], [], privkey=author_priv, sc=ind)
        log.info(f'created sc with index {ind} connected to tnx {tnxind}')
        return ind, tnxind

    def get_block(self, i, sync_get):
        """
        Return full block (In local blockchain might be only unfilled copy of block i (UnfilledBlock),
        then get full block from other peer)
        :param i: block's index
        :type i: int
        :param sync_get: function than gets object (block, transaction, smart contract) from network
        :type sync_get: function
        :return: Block
        """
        if not self[i].is_unfilled:
            return self[i]
        else:
            return sync_get(json.dumps([{'type': 'block', 'index': i}]))

    def add_miner(self, miner):
        """
        add proof-of-work miner
        miner = [hash, n, address, t]
        :param list miner: miner
        """
        b = self[-1]
        b.powminers.append(miner)
        self[-1] = b

    def add_sc(self, sc):
        """
        Add smart contract
        :param sc: smart contract to add
        :return: index of added sc
        :rtype: list or tuple
        """
        b = self[-1]
        b.contracts.append(sc)
        self[-1] = b
        ind = len(self) - 1, len(self[-1].sc) - 1
        return ind

    def pubkey_by_nick(self, nick, maxn=('l', 'l')):
        """
        Nicks can be used in transactions. Nicks can be defined in transaction with author=pubkey;nick;
        Nick can be transfered in transaction with autor=pubkey;nick;new pubkey;
        :param nick: str: pubkey, nick or nick definition
        :param maxn: tuple: maximum index or ('l', 'l') for entire blockchain
        :return: str: pubkey
        """
        if ';' not in nick and '[' not in nick and len(nick) > 20:
            return nick
        elif '[' in nick and ';' not in nick:
            return nick
        if nick.count(';') >= 2:
            return nick.split(';')[0]
        o = None
        for tnx in self.tnxiter(maxn=maxn):
            if tnx.author.endswith(nick + ';'):
                o = tnx.author.split(';')[0]
            elif ';' in tnx.author:
                if tnx.author.count(';') == 3 and tnx.author.split(';')[1] == nick:
                    o = tnx.author.split(';')[1]
        return o

    def has_traffic_rest(self, user, time_to, price, mined_hash=None):
        """
        HODL has no commission, so, to avoid spam, user has limit of actions in proportion to his balance.
        Next actions must be mined by this user. (todo)
        :param user: author of action to confirm
        :type user: str
        :param time_to: time of action (index of last tnx at than moment)
        :type time_to: list[int]
        :param price: price of the action
        :type price: float
        :param mined_hash: mined hash for mined actions
        :type mined_hash: int
        :return: validness of the action
        :rtype: bool
        """
        m = self.money(user, time_to)
        # todo: count all action prices
        return True

    def __repr__(self):
        return str([[len(b.txs), len(b.contracts)] for b in self])

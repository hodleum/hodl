from block import Blockchain as block
import wallet
import sync
from tests.testnet.roles import Alice, Bob, Chuck, Dave, miner, evil_miner
import os
import json
import multiprocessing
import time
import logging as log


# Alice, Bob, Chuck, Dave are creating clear blockchain with genesis block
# After that Alice creates transaction & waits for synchronization(other are waiting while net.py is doing it)
# Two seconds later Bob creates block & sends it to Alice & Chuck


with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
wallet.bch.clean()

with open('tests/genblock.bl', 'r') as f:
    wallet.bch.append(block.Block.from_json(f.readline()))


def main(name):
    log.basicConfig(level=log.DEBUG, format=name + ':%(module)s:%(lineno)d:%(message)s')
    log.debug('loop started; len(bch): '+str(len(wallet.bch))+', len(bch[0]): '+str(len(wallet.bch[0].txs)))
    # start tester thread (for example for Alice, Bob etc.)
    if name == 'Alice':
        my_wallet = wallet.new_wallet(keys['Alice'])
        Alice.main(wallet, keys)
    elif name == 'Bob':
        my_wallet = wallet.new_wallet(keys['Bob'])
        Bob.main(wallet, keys)
    elif name == 'Chuck':
        my_wallet = wallet.new_wallet(keys['Chuck'])
        Chuck.main(wallet, keys)
    elif name == 'Dave':
        my_wallet = wallet.new_wallet(keys['Dave'])
        Dave.main(wallet, keys)
    elif name == 'miner':
        my_wallet = wallet.new_wallet(keys['miner'])
        miner.main(wallet, keys)
    elif name == 'evil_miner':
        my_wallet = wallet.new_wallet(keys['evil_miner'])
        evil_miner.main(wallet, keys)


multiprocessing.Process(target=main, args=('Alice',), name='Alice').start()
multiprocessing.Process(target=main, args=('Bob',), name='Bob').start()
multiprocessing.Process(target=main, args=('Chuck',), name='Chuck').start()
multiprocessing.Process(target=main, args=('Dave',), name='Dave').start()
multiprocessing.Process(target=main, args=('miner',), name='miner').start()
multiprocessing.Process(target=main, args=('evil_miner',), name='evil_miner').start()
input()

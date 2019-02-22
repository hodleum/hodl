#!/usr/bin/python3
import os
from hodl import block
from hodl import wallet
from tests.testnet.roles import Alice, Bob, Chuck, Dave, miner, evil_miner
import json
from threading import RLock
import logging as log
import sys


# Alice, Bob, Chuck, Dave are creating clear blockchain with genesis block
# After that Alice creates transaction & waits for synchronization(other are waiting while net.py is doing it)
# Two seconds later Bob creates block & sends it to Alice & Chuck


lock = RLock()
with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())


def main(name):
    log.basicConfig(level=log.DEBUG, format=name + ':%(asctime)s:%(module)s:%(lineno)d:%(message)s', stream=sys.stdout)
    # start tester thread (for example for Alice, Bob etc.)
    if name == 'Alice':
        wallet.bch.clean()
        with open('tests/genblock.bl', 'r') as f:
            wallet.bch.append(block.Block.from_json(f.readline()))
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
    elif name == 'miner0':
        my_wallet = wallet.new_wallet(keys['miner0'])
        miner.main(wallet, keys['miner0'])
    elif name == 'miner1':
        my_wallet = wallet.new_wallet(keys['miner1'])
        miner.main(wallet, keys['miner1'])
    elif name == 'miner2':
        my_wallet = wallet.new_wallet(keys['miner2'])
        miner.main(wallet, keys['miner2'])
    elif name == 'evil_miner':
        my_wallet = wallet.new_wallet(keys['evil_miner'])
        evil_miner.main(wallet, keys)


main(os.getenv('HODL_NAME'))

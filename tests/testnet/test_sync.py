import block
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


name = str(os.getenv('HODL_NAME'))
log.basicConfig(level=log.DEBUG, format='%(module)s:%(lineno)d:%(message)s')
with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
my_keys = keys[name]
if name == 'Alice':
    # set public key and peers
    time.sleep(2)
if name == 'Bob':
    # set public key and peers
    pass
if name == 'Chuck':
    # set public key and peers
    pass
if name == 'Dave':
    # set public key and peers
    pass
my_wallet = wallet.new_wallet(my_keys, filename=name+'.db')
wallet.bch.clean()

with open('tests/genblock.bl', 'r') as f:
    wallet.bch.append(block.Block.from_json(f.readline()))


def main():
    log.debug('loop started; len(bch): '+str(len(wallet.bch))+', len(bch[0]): '+str(len(wallet.bch[0].txs)))
    # todo: start sync thread
    # start tester thread (for example for Alice, Bob etc.)
    if name == 'Alice':
        Alice.main(wallet, keys)
    elif name == 'Bob':
        Bob.main(wallet, keys)
    elif name == 'Chuck':
        Chuck.main(wallet, keys)
    elif name == 'Dave':
        Dave.main(wallet, keys)
    elif name == 'miner':
        miner.main(wallet, keys)
    elif name == 'evil_miner':
        evil_miner.main(wallet, keys)


multiprocessing.Process(target=main).start()
sync.handle.loop(my_keys,)

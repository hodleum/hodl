import os
import json
import multiprocessing
import time
import logging as log
import block
from net.peers import Peer, Peers
from sync import handle


# Alice, Bob, Chuck, Dave are creating clear blockchain with genesis block
# After that Alice creates transaction & waits for synchronization(other are waiting while net.py is doing it)
# Two seconds later Bob creates block & sends it to Alice & Chuck


name = str(os.getenv('HODL_NAME'))
bch = block.Blockchain(filename=name+'.db')
bch.clean()
log.basicConfig(filename=name+'.log', level=log.DEBUG)
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
port = 5000

with open('tests/genblock.bl', 'r') as f:
    bch.append(block.Block.from_json(f.readline()))
handle.loop(my_keys,)


def main():
    log.debug('loop started; len(bch): '+str(len(bch))+', len(bch[0]): '+str(len(bch[0].txs)))
    if name == 'Alice':
        bch.new_transaction(my_keys[1], [0, 0], [keys['Bob']], [1], privkey=my_keys[0])
        log.debug('tnx created')
    log.debug('st2; len(bch): '+str(len(bch))+', len(bch[0]): '+str(len(bch[0].txs)))
    time.sleep(2)
    log.debug('slept; len(bch): '+str(len(bch))+', len(bch[0]): '+str(len(bch[0].txs)))
    if name == 'Bob':
        bch.append(block.Block())
    log.debug('fin; len(bch): '+str(len(bch))+', len(bch[0]): '+str(len(bch[0].txs)))


multiprocessing.Process(target=main).start()

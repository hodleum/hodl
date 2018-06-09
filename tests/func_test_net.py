import os
import json
import multiprocessing
import time
import logging as log
import block
import net
import sync


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
    sync.peers = sync.Peers([sync.Peer(keys['Bob'][1], 'localhost', 5002),
                             sync.Peer(keys['Chuck'][1], 'localhost', 5003),
                             sync.Peer(keys['Dave'][1], 'localhost', 5004)])
    port = 5001
if name == 'Bob':
    sync.peers = sync.Peers([sync.Peer(keys['Alice'][1], 'localhost', 5001),
                             sync.Peer(keys['Chuck'][1], 'localhost', 5003),
                             sync.Peer(keys['Dave'][1], 'localhost', 5004)])
    port = 5002
if name == 'Chuck':
    sync.peers = sync.Peers([sync.Peer(keys['Bob'][1], 'localhost', 5002),
                             sync.Peer(keys['Alice'][1], 'localhost', 5001),
                             sync.Peer(keys['Dave'][1], 'localhost', 5004)])
    port = 5003
if name == 'Dave':
    sync.peers = sync.Peers([sync.Peer(keys['Bob'][1], 'localhost', 5002),
                             sync.Peer(keys['Chuck'][1], 'localhost', 5003),
                             sync.Peer(keys['Alice'][1], 'localhost', 5001)])
    port = 5004
with open('tests/genblock.bl', 'r') as f:
    bch.append(block.Block.from_json(f.readline()))
loop = multiprocessing.Process(target=sync.loop, args=(my_keys, port))
loop.start()
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

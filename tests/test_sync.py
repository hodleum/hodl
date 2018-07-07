import os
import json
import multiprocessing
import time
import logging as log
import block
from net.peers import Peer, Peers
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
    peers = Peers([Peer(keys['Bob'][1], [('172.19.0.2', 5000)]),
                             Peer(keys['Chuck'][1], [('172.19.0.3', 5000)]),
                             Peer(keys['Dave'][1], [('172.19.0.4', 5000)])])
    time.sleep(2)
if name == 'Bob':
    peers = Peers([Peer(keys['Alice'][1], [('172.19.0.1', 5000)]),
                             Peer(keys['Chuck'][1], [('172.19.0.3', 5000)]),
                             Peer(keys['Dave'][1], [('172.19.0.4', 5000)])])
if name == 'Chuck':
    peers = Peers([Peer(keys['Bob'][1], [('172.19.0.2', 5000)]),
                             Peer(keys['Alice'][1], [('172.19.0.1', 5000)]),
                             Peer(keys['Dave'][1], [('172.19.0.4', 5000)])])
if name == 'Dave':
    peers = Peers([Peer(keys['Bob'][1], [('172.19.0.2', 5000)]),
                             Peer(keys['Chuck'][1], [('172.19.0.3', 5000)]),
                             Peer(keys['Alice'][1], [('172.19.0.1', 5000)])])
port = 5000

with open('tests/genblock.bl', 'r') as f:
    bch.append(block.Block.from_json(f.readline()))
loop = multiprocessing.Process(target=sync.loop, args=(my_keys, port, log))
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

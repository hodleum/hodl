import os
import json
import multiprocessing
import time
import logging as log
import block
from net.Peers import Peer, Peers
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
    peers = Peers([Peer(keys['Bob'][1], [('192.168.200.200', 5002)]),
                             Peer(keys['Chuck'][1], [('192.168.200.200', 5003)]),
                             Peer(keys['Dave'][1], [('192.168.200.200', 5004)])])
    port = 5001
if name == 'Bob':
    peers = Peers([Peer(keys['Alice'][1], [('192.168.200.200', 5001)]),
                             Peer(keys['Chuck'][1], [('192.168.200.200', 5003)]),
                             Peer(keys['Dave'][1], [('192.168.200.200', 5004)])])
    port = 5002
if name == 'Chuck':
    peers = Peers([Peer(keys['Bob'][1], [('192.168.200.200', 5002)]),
                             Peer(keys['Alice'][1], [('192.168.200.200', 5001)]),
                             Peer(keys['Dave'][1], [('192.168.200.200', 5004)])])
    port = 5003
if name == 'Dave':
    peers = Peers([Peer(keys['Bob'][1], [('192.168.200.200', 5002)]),
                             Peer(keys['Chuck'][1], [('192.168.200.200', 5003)]),
                             Peer(keys['Alice'][1], [('192.168.200.200', 5001)])])
    port = 5004

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

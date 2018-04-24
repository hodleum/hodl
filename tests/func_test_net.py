import os
import block
import json
import multiprocessing
import net
import time
import logging as log

#Alice, Bob, Chuck, Dave are creating clear blockchain with genesis block
#After that Alice creates transaction & waits for synchronization(other are waiting while net.py is doing it)
#Two seconds later Bob creates block & sends it to Alice & Chuck


name = str(os.getenv('HODL_NAME'))
bch = block.Blockchain(filename=name+'.db') 
log.basicConfig(filename=name+'.log', level=log.DEBUG)
with open('file.txt', 'w') as f:
    pass
with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
my_keys = keys[name]
if name == 'Alice':
    net.peers = net.Peers([net.Peer(keys['Bob'], 'localhost', 5002), net.Peer(keys['Chuck'], 'localhost', 5003), net.Peer(keys['Dave'], 'localhost', 5004)])
if name == 'Bob':
    net.peers = net.Peers([net.Peer(keys['Alice'], 'localhost', 5001), net.Peer(keys['Chuck'], 'localhost', 5003), net.Peer(keys['Dave'], 'localhost', 5004)])
if name == 'Chuck':
    net.peers = net.Peers([net.Peer(keys['Bob'], 'localhost', 5002), net.Peer(keys['Alice'], 'localhost', 5001), net.Peer(keys['Dave'], 'localhost', 5004)])
if name == 'Dave':
    net.peers = net.Peers([net.Peer(keys['Bob'], 'localhost', 5002), net.Peer(keys['Chuck'], 'localhost', 5003), net.Peer(keys['Alice'], 'localhost', 5001)])
with open('tests/genblock.bl', 'r') as f:
    bch[0] = block.Block.from_json(f.readline())
loop = multiprocessing.Process(target=net.loop, args=tuple(my_keys))
log.debug('test')
loop.start()
log.debug('test1')
loop.join()
log.debug('test')
if name == 'Alice':
    bch.new_transaction(my_keys[1], [0, 0], [keys['Bob']], [1], privkey=my_keys[0])
time.sleep(2)
if name == 'Bob':
    bch.append(block.Block())
log.debug(name, bch[0].txs[1].__dict__)
log.debug(bch[1])

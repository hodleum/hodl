import os
import block
import json
import multiprocessing
import net
import time


#Alice, Bob, Chuck, Dave are creating clear blockchain with genesis block
#After that Alice creates transaction & waits for synchronization(other are waiting while net.py is doing it)
#Two seconds later Bob creates block & sends it to Alice & Chuck


bch = block.Blockchain()
name = os.getenv('HODL_NAME')
with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
my_keys = keys[name]
with open('tests/genblock.bl', 'r') as f:
    bch[0] = block.Block.from_json(f.readline())
loop = multiprocessing.Process(target=net.loop(), args=tuple())
loop.start()
loop.join()
if name == 'Alice':
    bch.new_transaction(my_keys[1], [0, 0], [keys['Bob']], [1], privkey=my_keys[0])
time.sleep(2)
if name == 'Bob':
    bch.append(block.Block())
print(name, bch[0].txs[1].__dict__)
print(bch[1])

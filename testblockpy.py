import block
import cryptogr as cg1


bch = block.Blockchain()
nblocks = 5
block.cg.f = ['priv.key', 'pub.key']
block.cg.genkeys()
for i in range(nblocks):
    bch.new_block(0, block.cg.keys()[0])
if not bch.money(block.cg.keys()[0]) == nblocks:
    print('Не работает(12)')
txn = block.Transaction()
txn.gen(block.cg.keys()[0], [(0,0)], [cg1.keys()[0]], [1], (0,1))
bch.blocks[0].append(txn, bch)
if not bch.money(block.cg.keys()[0]) == nblocks-1:
    print('не работает (17)')

import unittest
import block
import cryptogr as cg
import json
import wallet


class TestFunc(unittest.TestCase):
    def test_func(self):
        my_keys = cg.gen_keys()
        my_wallet = wallet.Wallet(my_keys)
        your_pub_key = cg.gen_keys()[1]
        wallet.bch.clean()
        with open('tests/keys', 'r') as f:
            keys = json.loads(f.readline())
        with open('tests/genblock.bl', 'r') as f:
            wallet.bch.append(block.Block.from_json(f.readline()))
        wallet.bch.new_transaction(keys['Alice'][1], [[0, 0]], [my_keys[1], keys['Alice'][1]], [0.95, 0.05], 'signing', keys['Alice'][0])
        wallet.bch.new_transaction(keys['Bob'][1], [[0, 0]], [my_keys[1]], [1], 'signing', keys['Bob'][0])
        wallet.bch.new_transaction(keys['Chuck'][1], [[0, 0]], [my_keys[1], keys['Chuck'][1]], [0.95, 0.05], 'signing', keys['Chuck'][0])
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])

        n = 1000
        n, t, h = block.mining.pow_mine(wallet.bch, 90000000000000000000000000000000000, my_keys[1])
        wallet.bch.add_miner([int(h), n, my_keys[1], t])
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        my_wallet.new_transaction(['sc[1, 0]'+'payment'], [1])
        my_wallet.new_transaction(['sc[1, 0]'], [0.1])
        wallet.bch.append(block.mining.mine(wallet.bch))
        # todo: processing txs with the same address several times in outs
        my_wallet.new_transaction([your_pub_key, my_keys[1]], [0.5, wallet.bch[1].txs[0].outns[0]-0.5])
        print(wallet.bch.money(my_keys[1]))
        with open('tests/scex.py', 'r') as f:
            wallet.bch.new_sc(f.readlines(), my_keys[1], my_keys[0], memsize=10000520)
        wallet.bch.commit()
        b = wallet.bch[1]
        b.contracts[0].execute()
        b.contracts[0].msgs.append(['sell', (my_keys[1], 0.05), str(list(cg.sign(json.dumps(['sell', (str(my_keys[1]), 0.05)]), my_keys[0]))), False])
        wallet.bch[1] = b
        cc = block.Blockchain()[0].contracts
        b.contracts[0].handle_messages()
        wallet.bch[1] = b
        self.assertAlmostEqual(0.05, json.loads(b.contracts[0].memory.local)[0][my_keys[1]])
        v = wallet.bch.is_valid()
        self.assertTrue(v)
        b.contracts[0].memory += '{}fads;"[]'*1000001
        b.contracts[0].memory.peers = [my_keys[1], your_pub_key, '1', '2', '3', '4', '5', '6', '7', '8', '9']
        b.contracts[0].memory.distribute_peers()
        wallet.bch[1] = b
        self.assertEqual(len(b.contracts[0].memory.accepts), 3)
        self.assertTrue(b.contracts[0].is_valid(wallet.bch))
        wallet.bch.new_transaction(keys['Chuck'][1], [[0, 0]], [my_keys[1]], [0.05], 'signing', keys['Chuck'][0])
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        n = 1000
        n, t, h = block.mining.pow_mine(wallet.bch, 90000000000000000000000000000000000, my_keys[1])
        wallet.bch.add_miner([int(h), n, my_keys[1], t])
        wallet.bch.append(block.mining.mine(wallet.bch))
        # tests of SC tasks distribution and mining
        print('my money', wallet.bch.money(my_keys[1]))
        print('your money', wallet.bch.money(your_pub_key))
        print('Passed!')


unittest.main()

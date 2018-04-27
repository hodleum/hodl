import unittest
import block
import cryptogr as cg
import json


class TestFunc(unittest.TestCase):
    def test_func(self):
        my_keys = cg.gen_keys()
        your_pub_key = cg.gen_keys()[1]
        bch = block.Blockchain()
        bch.clean()
        with open('tests/keys', 'r') as f:
            keys = json.loads(f.readline())
        with open('tests/genblock.bl', 'r') as f:
            bch.append(block.Block.from_json(f.readline()))
        bch.new_transaction(keys['Alice'][1], [[0, 0]], [my_keys[1], keys['Alice'][1]], [0.95, 0.05], 'signing', keys['Alice'][0])
        bch.new_transaction(keys['Bob'][1], [[0, 0]], [my_keys[1]], [1], 'signing', keys['Bob'][0])
        bch.new_transaction(keys['Chuck'][1], [[0, 0]], [my_keys[1]], [1], 'signing', keys['Chuck'][0])
        bch.new_transaction(my_keys[1], [[0, 1]], ['mining', my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])

        n = 1000
        n, t, h = block.mining.pow_mine(bch, 90000000000000000000000000000000000, my_keys[1])
        bch.add_miner([int(h), n, my_keys[1], t])
        bch.new_transaction(my_keys[1], [[0, 1]], ['mining', my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [[0, 1]], ['mining', my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [[0, 1]], ['mining', my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [[0, 2]], ['sc[1, 0]'+'payment'], [1], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [[0, 0], [1, 0]], [your_pub_key, my_keys[1]], [0.5, 0.3], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [[0, 1]], ['sc[1, 0]'], [0.1], privkey=my_keys[0])
        bch.append(block.mining.mine(bch))
        with open('tests/scex.py', 'r') as f:
            bch.new_sc(f.readlines(), my_keys[1], my_keys[0], memsize=10000520)
        bch.commit()
        b = bch[1]
        b.contracts[0].execute()
        b.contracts[0].msgs.append(['sell', (my_keys[1], 0.05), str(list(cg.sign(json.dumps(['sell', (str(my_keys[1]), 0.05)]), my_keys[0]))), False])
        bch[1] = b
        cc = block.Blockchain()[0].contracts
        b.contracts[0].handle_messages()
        bch[1] = b
        self.assertAlmostEqual(0.05, json.loads(b.contracts[0].memory.local)[0][my_keys[1]])
        v = bch.is_valid()
        self.assertTrue(v)
        b.contracts[0].memory += '{}fads;"[]'*1000001
        b.contracts[0].memory.peers = [my_keys[1], your_pub_key, '1', '2', '3', '4', '5', '6', '7', '8', '9']
        b.contracts[0].memory.distribute_peers()
        bch[1] = b
        self.assertEqual(len(b.contracts[0].memory.accepts), 3)
        self.assertTrue(b.contracts[0].is_valid(bch))
        bch.append(block.mining.mine(bch))
        # tests of SC tasks distribution and mining
        print('Passed!')


unittest.main()

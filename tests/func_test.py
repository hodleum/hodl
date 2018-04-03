import unittest
import block
import cryptogr as cg
import json


class TestFunc(unittest.TestCase):
    def test_func(self):
        my_keys = cg.gen_keys()
        your_pub_key = cg.gen_keys()[1]
        bch = block.Blockchain()
        with open('tests/keys', 'r') as f:
            keys = json.loads(f.readline())
        with open('tests/genblock.bl', 'r') as f:
            bch[0] = block.Block.from_json(f.readline())
        bch.clean()
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        bch.new_transaction(my_keys[1], [[0, 0], [1, 0]], [your_pub_key, my_keys[1]], [0.5, 0.3], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [[0, 0]], ['sc[0, 0]'], [0.1], privkey=my_keys[0])
        with open('tests/scex.py', 'r') as f:
            bch.new_sc(f.readlines(), my_keys[1], my_keys[0])
        bch = block.Blockchain()
        b = bch[0]
        b.contracts[0].execute()
        b.contracts[0].msgs.append(['sell', (my_keys[1], 0.05), str(list(cg.sign(json.dumps(['sell', (str(my_keys[1]), 0.05)]), my_keys[0]))), False])
        bch[0] = b
        bch.conn.commit()
        b.contracts[0].handle_messages()
        bch[0] = b
        self.assertEqual(0.05, json.loads(b.contracts[0].memory.local)[0][my_keys[1]])
        b.contracts[0].memory += '{}fadffkjlds;da""[]'*20000000
        b.contracts[0].memory.peers = [my_keys[1], your_pub_key, '1', '2', '3', '4', '5', '6', '7', '8', '9']
        b.contracts[0].memory.distribute_peers()
        self.assertEqual(b.contracts[0].memory.accepts[2], {'1': []})
        print('Passed!')


unittest.main()

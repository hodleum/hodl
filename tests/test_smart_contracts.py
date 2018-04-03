import block
import unittest
import cryptogr as cg
import json
import os
try:
    os.mkdir('tmp')
except:
    pass


my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]


class TestSmartContracts(unittest.TestCase):
    def test_sc_create_and_exec(self):
        bch = block.Blockchain()
        bch.clean()
        bch.new_block([my_keys[1], your_pub_key])
        with open('tests/scex.py', 'r') as f:
            sc = block.Smart_contract(f.readlines(), my_keys[1], [0, 0])
        sc.sign_sc(my_keys[0])
        bch.add_sc(sc)
        bch = block.Blockchain()
        b = bch[0]
        b.contracts[0].execute()
        self.assertEqual([{'0': 0.2}, 1, 1], json.loads(b.contracts[0].memory.local))

    def test_sc_msg(self):
        bch = block.Blockchain()
        bch.clean()
        bch.new_block([my_keys[1], your_pub_key])
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

    def test_str_encoding(self):
        with open('tests/scex.py', 'r') as f:
            sc = block.Smart_contract(f.readlines(), my_keys[1], [0, 0])
        sc.sign_sc(my_keys[0])
        sc2 = block.Smart_contract.from_json(str(sc))
        self.assertTrue(sc == sc2)

    def test_sc_memory_str(self):
        block.sc_base_mem = 10
        m = block.SCMemory([0, 0], block.sc_base_mem)
        m.local = '{}fadffkjlds;da""dsakfdjkfdsalkjfdslkjfdsalkjfdlkjfds[]'
        self.assertEqual(m.local, block.SCMemory.from_json(str(m)).local)

    def test_sc_memory_distribution(self):
        m = block.SCMemory([0, 0], block.sc_base_mem)
        m.size = 20000000000
        m += '{}fadffkjlds;da""[]'*20000000
        m.peers = [my_keys[1], your_pub_key, '1', '2', '3', '4', '5', '6', '7', '8', '9']
        m.distribute_peers()
        self.assertEqual(m.accepts[2], {'1': []})


if __name__ == '__main__':
    unittest.main()

import block
import unittest
import cryptogr as cg
import json


my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]


class TestSmartContracts(unittest.TestCase):
    def test_sc_create_and_exec(self):
        bch = block.Blockchain()
        bch.clean()
        bch.new_block([my_keys[1], your_pub_key])
        sc = block.Smart_contract(open('scex.py', 'r').readlines(), my_keys[1], (0, 0))
        sc.sign_sc(my_keys[0])
        bch.add_sc(sc)
        bch = block.Blockchain()
        b = bch[0]
        b.contracts[0].execute()
        print(b.contracts[0].memory)

    def t_sc_msg(self):
        bch = block.Blockchain()
        bch.clean()
        bch.new_block([my_keys[1], your_pub_key])
        sc = block.Smart_contract(open('scex.py', 'r').readlines(), my_keys[1], [0, 0])
        sc.sign_sc(my_keys[0])
        bch.add_sc(sc)
        bch = block.Blockchain()
        bch.new_transaction(my_keys[1], [[0, 0]], ['sc[0, 0]'], [0.1], privkey=my_keys[0])
        b = bch[0]
        b.contracts[0].msgs.append(['sell', (my_keys[1], 0.05), str(list(cg.sign(json.dumps(['sell', (str(my_keys[1]), 0.05)]), my_keys[0])))])
        bch[0] = b
        print(b.contracts[0].memory)

    def test_str_encoding(self):
        sc = block.Smart_contract(open('scex.py', 'r').readlines(), my_keys[1], (0, 0))
        sc.sign_sc(my_keys[0])
        self.assertTrue(sc == block.Smart_contract.from_json(str(sc)))


if __name__ == '__main__':
    unittest.main()

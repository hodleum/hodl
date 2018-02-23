import block
import unittest
import cryptogr as cg


my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]
class TestSmartContracts(unittest.TestCase):
    def test_sc(self):
        bch = block.Blockchain()
        bch.clean()
        bch.new_block([my_keys[1], your_pub_key])
        bch.add_sc(block.Smart_contract(open('scex.py', 'r').readlines(), my_keys[1], (0, 0)))
        bch[0].contracts[0].execute()

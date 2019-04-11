import unittest
from hodl import block
from hodl import cryptogr as cg
from threading import Lock
from unittest.mock import sentinel, MagicMock, patch
from hodl.block.Blockchain import genblock
import os
import json


# todo: write tests


with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
os.system('rm db/bch.db')
my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]
bch = block.Blockchain()


class TestBlockchain(unittest.TestCase):
    def test_blockchain_creation_and_block_addition(self):
        bch[0] = genblock
        bch.append(genblock)
        self.assertEqual(len(bch), 2)

    def test_index(self):
        self.assertEqual(bch.index(bch[1]), 1)

    def test_tnxiter(self):
        self.assertEqual(len(list(bch.tnxiter())), 4)
        self.assertEqual(len(list(bch.tnxiter([1, 0]))), 2)
        self.assertEqual(len(list(bch.tnxiter(fr=[1, 0]))), 2)
        self.assertEqual(list(bch.tnxiter(fr=[1, 0]))[0], bch[1, 0])

    def test_money_counter(self):
        self.assertEqual(bch.money(keys['Alice'][1]), 2)

    def test_iter(self):
        self.assertEqual([b for b in bch][0], bch[0])
        self.assertEqual(len([b for b in bch]), len(bch))


class TestBlock(unittest.TestCase):
    def test_block_str_encoding(self):
        self.assertEqual(genblock, block.Block.from_json(str(genblock)))


class TestTnx(unittest.TestCase):
    def test_tnx_str_encoding(self):
        tnx = genblock.txs[0]
        self.assertEqual(tnx, block.Transaction.from_json(str(tnx)))


if __name__ == '__main__':
    unittest.main(verbosity=2)

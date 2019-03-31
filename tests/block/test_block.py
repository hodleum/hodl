import unittest
from hodl import block
from hodl import cryptogr as cg
from threading import Lock
from unittest.mock import sentinel, MagicMock, patch
from hodl.block.Blockchain import genblock
import os


os.system('rm db/bch.db')
my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]
bch = block.Blockchain()


class BlockchainUnittest(unittest.TestCase):
    def test_blockchain_creation_and_block_addition(self):
        bch.append(genblock)
        bch.append(genblock)
        self.assertEqual(len(bch), 2)


class TestBlock(unittest.TestCase):
    def test_block_str_encoding(self):
        self.assertEqual(genblock, block.Block.from_json(str(genblock)))


class TestTnx(unittest.TestCase):
    def test_tnx_str_encoding(self):
        tnx = genblock.txs[0]
        self.assertEqual(tnx, block.Transaction.from_json(str(tnx)))


if __name__ == '__main__':
    unittest.main(verbosity=2)

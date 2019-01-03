import unittest
from hodl import block
from hodl import cryptogr as cg
import time
from itertools import chain
from unittest.mock import sentinel, MagicMock, patch

my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]
with open('tests/genblock.bl', 'r') as f:
    genblock = block.Block.from_json(f.readline())


class BlockchainUnittest(unittest.TestCase):
    def test_block_iter(self):
        bch = block.Blockchain()
        bch.clean()
        bch.append(genblock)
        bch.append(genblock)
        self.assertEqual(len([b for b in bch]), len(bch))
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

import unittest
import block
import cryptogr as cg
import time
from itertools import chain
from unittest.mock import sentinel, MagicMock, patch


my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]


class BlockUnittest(unittest.TestCase):
    def test_block_iter(self):
        bch = block.Blockchain()
        bch.clean()
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        self.assertEqual(len([b for b in bch]), len(bch))
        self.assertEqual(len(bch), 2)

    def test_creations_and_money_counter(self):
        bch = block.Blockchain()
        bch.clean()
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        self.assertEqual(len(bch), 2)
        self.assertEqual(len([b for b in bch]), 2)
        bch.new_transaction(my_keys[1], [[0, 0], [1, 0]], [your_pub_key, my_keys[1]], [0.5, 0.3], 'signing', my_keys[0])
        self.assertAlmostEqual(bch.money(my_keys[1]), 0.3)
        self.assertAlmostEqual(bch.money(your_pub_key), 1.7)
        bch.conn.close()

    def test_block_str_encoding(self):
        bch = block.Blockchain()
        bch.clean()
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        bch.new_transaction(my_keys[1], [[0, 0], [1, 0]], [your_pub_key, my_keys[1]], [0.5, 0.3], 'signing', my_keys[0])
        b2 = block.Block.from_json(str(bch[1]))
        d = bch[1].__dict__
        d1 = b2.__dict__
        for k in d.keys():
            if d[k]!=d1[k]:
                print(k, d[k], d1[k])
        print(bch[1].txs, b2.txs)
        self.assertEqual(b2, bch[1])
        bch.conn.close()

    def test_tnx_str_encoding(self):
        bch = block.Blockchain()
        bch.clean()
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        bch.new_transaction(my_keys[1], [[0, 0], [1, 0]], [your_pub_key, my_keys[1]], [0.5, 0.3], 'signing', my_keys[0])
        b2 = block.Transaction().from_json(str(bch[1].txs[0]))
        self.assertEqual(b2, bch[1].txs[0])
        bch.conn.close()


class TestPrevhash(unittest.TestCase):
    def test_empty_empty(self):
        self.assertEqual('0', block.get_prevhash([], []))

    def test_empty_something(self):
        self.assertEqual('0', block.get_prevhash([], ['1', '2', '3']))

    def test_something_something(self):
        blockchain = [MagicMock(), MagicMock(h=sentinel.hash)]
        self.assertEqual(sentinel.hash, block.get_prevhash(blockchain, ['1', '2', '3']))


class TestBlock(unittest.TestCase):
    @patch('block.Block.update')
    def test_init_of_blocks(self, m_update):
        b = block.Block()
        self.assertTrue(hasattr(b, 'n'))
        self.assertTrue(hasattr(b, 'prevhash'))
        self.assertTrue(hasattr(b, 'timestamp'))
        self.assertTrue(hasattr(b, 'txs'))
        self.assertTrue(hasattr(b, 'contracts'))
        self.assertTrue(hasattr(b, 'creators'))
        self.assertTrue(hasattr(b, 'powminers'))
        self.assertTrue(hasattr(b, 'powhash'))
        m_update.assert_called_with()


class TestHash(unittest.TestCase):
    def test_hash(self):
        self.assertEqual('2122914021714301784233128915223624866126', cg.h(''))
        self.assertEqual('20720532132149213101239102231223249249135100218', cg.h('0'))
        

class TestTimestamp(unittest.TestCase):
    @patch('block.time.time', return_value=5051)
    def test_now(self, m_time):
        self.assertEqual(5051, block.get_timestamp('now'))

    def test_fixed(self):
        self.assertEqual(15, block.get_timestamp('15'))


class TestPowHash(unittest.TestCase):
    def test_calculating_pow_hashing(self):
        self.assertEqual('142249934117814601051212461754312103119', block.Block.calc_pow_hash(block.Block()))


if __name__ == '__main__':
    unittest.main(verbosity=2)

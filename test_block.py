import unittest
import block
import cryptogr as cg
import time
from itertools import chain


my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]
class BlockUnittest(unittest.TestCase):
    def test_creations_and_money_counter(self):
        bch = block.Blockchain()
        bch.clean()
        print(len(bch), bch.money(my_keys[1]))
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        print(bch.money(my_keys[1]), len(bch))
        bch.new_block([my_keys[1], your_pub_key, your_pub_key])
        print(bch.money(my_keys[1]), bch[1].txs[0].timestamp, time.time())
        print(len(bch))
        bch.new_transaction(my_keys[1], [[0, 0], [1, 0]], [your_pub_key, my_keys[1]], [0.5, 0.3], 'signing', my_keys[0])
        print(bch.money(my_keys[1]))
        print(len(bch))
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
        b2 = block.Transaction()
        b2.from_json(str(bch[1].txs[0]))
        self.assertEqual(b2, bch[1].txs[0])
        bch.conn.close()



if __name__ == '__main__':
    unittest.main()

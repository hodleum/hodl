import unittest
import block
import cryptogr as cg


my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]
class BlockUnittest(unittest.TestCase):
    def test_creations_and_money_counter(self):
        bch = block.Blockchain()
        bch.new_block([my_keys[1], your_pub_key], [0.75, 0.25])
        bch.new_block([my_keys[1], your_pub_key], [0.85, 0.15])
        bch.new_transaction(my_keys[1], [(0, 0)], [your_pub_key, my_keys[1]], [0.5, 0.25], 'signing', my_keys[0])
        print(bch[0].txs[0].spent(bch))
        self.assertAlmostEqual(bch.money(my_keys[1]), 1.1)
        self.assertAlmostEqual(bch.money(your_pub_key), 0.9)
    def test_str_encoding(self):
        bch = block.Blockchain()
        bch.new_block([my_keys[1], your_pub_key], [0.75, 0.25])
        bch.new_block([my_keys[1], your_pub_key], [0.85, 0.15])
        bch.new_transaction(my_keys[1], [(0, 0)], [your_pub_key, my_keys[1]], [0.5, 0.25], 'signing', my_keys[0])
        bch2 = block.Blockchain
        bchstr = str(bch)
        bch2.fromstr(bchstr)
        assertEqual(bch2, bch)

if __name__ == '__main__':
    unittest.main()

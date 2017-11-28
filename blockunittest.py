import block
import unittest
import cryptogr as cg


my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]
bch = block.Blockchain()
class BlockUnittest(unittest.TestCase):
    def test_block_creation(self):
        bch.new_block([my_keys[1], your_pub_key], [0.75, 0.25])
        bch.new_block([my_keys[1], your_pub_key], [0.85, 0.15])
        bch.new_transaction(my_keys[1], [0, 0], [your_pub_key], [0.5], 'signing', my_keys[0])
        print(bch[1].txs[1].spent(bch))
        print(bch.money(my_keys[1]), 1.1)
        self.assertAlmostEqual(bch.money(my_keys[1]), 0.9)

if __name__ == '__main__':
    unittest.main()

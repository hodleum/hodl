import mining
import block
import cryptogr as cg
import unittest

bch = block.Blockchain()
my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]
bch.new_block([my_keys[1], your_pub_key], [0.75, 0.25])
bch.new_block([my_keys[1], your_pub_key], [0.85, 0.15])
bch.new_transaction(my_keys[1], [(0, 0)], [your_pub_key, my_keys[1]], [0.5, 0.25], 'signing', my_keys[0])
class MiningUnittest(unittest.TestCase):
    def test_pow(self):
        n, t = mining.pow_mine(bch, 3210400000000000000000000000000000000, my_keys[1])
        print(n, t)

    def test_poc(self):
        xs = mining.poc_mine(1000, bch, my_keys[1])
        print(len(xs), xs)


if __name__ == '__main__':
    unittest.main()

import mining
import block
import cryptogr as cg
import unittest
from unittest.mock import sentinel, patch, MagicMock


my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]
class MiningUnittest(unittest.TestCase):
    def test_pow(self):
        bch = block.Blockchain()
        bch.new_block([my_keys[1], my_keys[1], your_pub_key])
        bch.new_block([my_keys[1], my_keys[1], your_pub_key])
        bch.new_transaction(my_keys[1], [(0, 0)], [your_pub_key, my_keys[1]], [0.5, 0.25], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [(0, 0)], [your_pub_key, my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [(0, 0)], [your_pub_key, my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [(0, 0)], [your_pub_key, my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [(0, 0)], [your_pub_key, my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])
        n, t, h = mining.pow_mine(bch, 900000000000000000000000000000000000, my_keys[1])
        print(n, t, h)


    def test_mining(self):
        bch = block.Blockchain()
        bch.new_block([my_keys[1], my_keys[1], your_pub_key])
        bch.new_transaction(my_keys[1], [(0, 0)], [your_pub_key, my_keys[1]], [0.5, 0.25], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [(0, 0)], [your_pub_key, my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [(0, 0)], ['mining', my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [(0, 0)], ['mining', my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])
        bch.new_transaction(my_keys[1], [(0, 0)], ['mining', my_keys[1]], [0.05, 0.95], 'signing', my_keys[0])
        n = 1000
        n, t, h = mining.pow_mine(bch, 90000000000000000000000000000000000, my_keys[1])
        bch.add_miner([int(h), n, my_keys[1], t])
        bch.add_miner([int(h), n, my_keys[1], t])
        bch.add_miner([int(h), n, my_keys[1], t])
        bl = block.Block(n, [my_keys[1]], bch, [], [], t)
        b = mining.mine(bch)
        bch.append(b)
        print('n', bch[-1].n)
        self.assertTrue(mining.validate(bch, -1))


class TestMiningDeltaT(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(5, mining.mining_delta_t(0))
        self.assertEqual(7, mining.mining_delta_t(20000))
        self.assertEqual(42, mining.mining_delta_t(321456.5))

@patch('mining.validate_pow')
@patch('mining.validate_pos')
@patch('mining.validate_poc')
class TestValidate(unittest.TestCase):
    def test_everything_ok(self, m_poc, m_pos, m_pow):
        m_poc.return_value = m_pos.return_value = m_pow.return_value = True
        self.assertTrue(mining.validate(sentinel.bch, sentinel.i))
        m_poc.assert_called_with(sentinel.bch, sentinel.i)
        
    def test_everything_fails(self, m_poc, m_pos, m_pow):
        m_poc.return_value = m_pos.return_value = m_pow.return_value = False
        self.assertFalse(mining.validate(sentinel.bch, sentinel.i))
        m_pow.assert_called_with(sentinel.bch, sentinel.i)



if __name__ == '__main__':
    unittest.main(verbosity=2)

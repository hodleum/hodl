from hodl.block import mining
import hodl.block
import hodl.cryptogr as cg
import unittest
from unittest.mock import sentinel, patch, MagicMock

my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]


class MiningUnittest(unittest.TestCase):
    pass  # todo


if __name__ == '__main__':
    unittest.main(verbosity=2)

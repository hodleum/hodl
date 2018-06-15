import unittest
import block
import cryptogr as cg
import json
import wallet


class TestFunc(unittest.TestCase):
    def test_func(self):
        with open('tests/my_keys', 'r') as f:
            my_keys = json.loads(f.read())
        my_wallet = wallet.Wallet(my_keys)
        with open('tests/your_key', 'r') as f:
            your_pub_key = json.loads(f.read())
        wallet.bch.clean()
        with open('tests/keys', 'r') as f:
            keys = json.loads(f.readline())
        with open('tests/genblock.bl', 'r') as f:
            wallet.bch.append(block.Block.from_json(f.readline()))
        # 0 1
        wallet.bch.new_transaction(keys['Alice'][1], [[0, 0]], [my_keys[1], keys['Alice'][1]], [0.95, 0.05], 'signing', keys['Alice'][0])
        b = wallet.bch[0]
        b.txs[1].timestamp = 1520682153
        b.txs[1].update()
        wallet.bch[0] = b
        # 0 2
        wallet.bch.new_transaction(keys['Bob'][1], [[0, 0]], [my_keys[1]], [1], 'signing', keys['Bob'][0])
        b = wallet.bch[0]
        b.txs[2].timestamp = 1520682154
        b.txs[2].update()
        wallet.bch[0] = b
        # 0 3
        wallet.bch.new_transaction(keys['Chuck'][1], [[0, 0]], [my_keys[1], keys['Chuck'][1]], [0.95, 0.05], 'signing', keys['Chuck'][0])
        b = wallet.bch[0]
        b.txs[3].timestamp = 1520682155
        b.txs[3].update()
        wallet.bch[0] = b
        # 0 4
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        b = wallet.bch[0]
        b.txs[4].timestamp = 1520682156
        b.txs[4].update()
        wallet.bch[0] = b
        n = 1000
        n, t, h = block.mining.pow_mine(wallet.bch, 90000000000000000000000000000000000, my_keys[1])
        wallet.bch.add_miner([int(h), n, my_keys[1], t])
        # 0 5
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        b = wallet.bch[0]
        b.txs[5].timestamp = 1520682157
        b.txs[5].update()
        wallet.bch[0] = b
        # 0 6
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        b = wallet.bch[0]
        b.txs[6].timestamp = 1520682158
        b.txs[6].update()
        wallet.bch[0] = b
        # 0 7
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        b = wallet.bch[0]
        b.txs[7].timestamp = 1520682159
        b.txs[7].update()
        wallet.bch[0] = b
        # 0 8
        my_wallet.new_transaction(['sc[1, 0]'+'payment'], [1])
        b = wallet.bch[0]
        b.txs[8].timestamp = 1520682160
        b.txs[8].update()
        wallet.bch[0] = b
        # 0 9
        my_wallet.new_transaction(['sc[1, 0]'], [0.1])
        b = wallet.bch[0]
        b.txs[9].timestamp = 1520682161
        b.txs[9].update()
        wallet.bch[0] = b
        # 1 0, 1 1
        block.mining.time.time = lambda: 1520682452
        wallet.bch.append(block.mining.mine(wallet.bch))
        # todo: processing txs with the same address several times in outs
        # 1 2
        my_wallet.new_transaction([your_pub_key], [0.5])
        b = wallet.bch[1]
        b.txs[2].timestamp = 1520682453
        b.txs[2].update()
        wallet.bch[1] = b
        print(wallet.bch.money(my_keys[1]))
        with open('tests/scex.py', 'r') as f:
            wallet.bch.new_sc(f.readlines(), my_keys[1], my_keys[0], memsize=10000520)
        wallet.bch.commit()
        b = wallet.bch[1]
        b.contracts[0].execute()
        b.contracts[0].msgs.append(['sell', (my_keys[1], 0.05), str(list(cg.sign(json.dumps(['sell', (str(my_keys[1]), 0.05)]), my_keys[0]))), False])
        wallet.bch[1] = b
        cc = block.Blockchain()[0].contracts
        b.contracts[0].handle_messages()
        wallet.bch[1] = b
        self.assertAlmostEqual(0.05, json.loads(b.contracts[0].memory.local)[0][my_keys[1]])
        print('validness checking started. Bch has now', len(wallet.bch), 'blocks, last block has', len(wallet.bch[-1].txs), 'txs.')
        v = wallet.bch.is_valid()
        self.assertTrue(v)
        b.contracts[0].memory += '{}fads;"[]'*1000001
        b.contracts[0].memory.peers = [my_keys[1], your_pub_key, '1', '2', '3', '4', '5', '6', '7', '8', '9']
        b.contracts[0].memory.distribute_peers()
        wallet.bch[1] = b
        self.assertEqual(len(b.contracts[0].memory.accepts), 3)
        self.assertTrue(b.contracts[0].is_valid(wallet.bch))
        # 1 3
        wallet.bch.new_transaction(keys['Chuck'][1], [[0, 3]], [my_keys[1]], [0.05], 'signing', keys['Chuck'][0])
        print(my_wallet.my_money())
        b = wallet.bch[1]
        b.txs[3].timestamp = 1520682457
        b.txs[3].update()
        wallet.bch[1] = b
        # 1 4
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        b = wallet.bch[1]
        b.txs[4].timestamp = 1520682458
        b.txs[4].update()
        wallet.bch[1] = b
        print(my_wallet.my_money())
        # 1 5
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        b = wallet.bch[1]
        b.txs[5].timestamp = 1520682459
        b.txs[5].update()
        wallet.bch[1] = b
        # 1 6
        my_wallet.new_transaction(['mining', my_keys[1]], [0.05, 0.95])
        b = wallet.bch[1]
        b.txs[6].timestamp = 1520682460
        b.txs[6].update()
        wallet.bch[1] = b
        n = 1000
        n, t, h = block.mining.pow_mine(wallet.bch, 90000000000000000000000000000000000, my_keys[1])
        wallet.bch.add_miner([int(h), n, my_keys[1], t])
        # 2 0, 2 1
        wallet.bch.append(block.mining.mine(wallet.bch))
        # tests of SC tasks distribution and mining
        print('my money', wallet.bch.money(my_keys[1]))
        self.assertEqual(wallet.bch.money(my_keys[1]), 211.35)
        print('your money', wallet.bch.money(your_pub_key))
        self.assertEqual(wallet.bch.money(your_pub_key), 0.5)
        print('Passed!')


unittest.main()

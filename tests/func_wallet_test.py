import unittest
import logging as log
import json
import cryptogr as cg
import block
import mining
import wallet


log.basicConfig(level=log.DEBUG, format='%(module)s:%(lineno)d:%(message)s')


class TestFunc(unittest.TestCase):
    def test_func(self):
        with open('tests/my_keys', 'r') as f:
            my_keys = json.loads(f.read())
        my_wallet = wallet.new_wallet(my_keys)
        with open('tests/your_key', 'r') as f:
            your_pub_key = json.loads(f.read())[0]
        wallet.bch.clean()
        with open('tests/keys', 'r') as f:
            keys = json.loads(f.readline())
        with open('tests/genblock.bl', 'r') as f:
            wallet.bch.append(block.Block.from_json(f.readline()))
        # 0 1
        wallet.bch.new_transaction(keys['Alice'][1], [[0, 0]], [my_keys[1], keys['Alice'][1]], [0.95, 0.05],
                                   'signing', keys['Alice'][0])
        log.info('me: ' + str(wallet.bch.money(my_keys[1])) + ', you: ' + str(wallet.bch.money(your_pub_key))
                 + ', Alice: ' + str(wallet.bch.money(keys['Alice'][1])) +
                 '. Len of bch: {}, of last block: {}'.format(str(len(wallet.bch)), str(len(wallet.bch[-1].txs)))
                 + '\n[{}, {}]'.format(str(len(wallet.bch)-1), str(len(wallet.bch[-1].txs)-1)))
        # 0 2
        wallet.bch.new_transaction(keys['Bob'][1], [[0, 0]], [my_keys[1]], [1], 'signing', keys['Bob'][0])
        log.info('me: ' + str(wallet.bch.money(my_keys[1])) + ', you: ' + str(wallet.bch.money(your_pub_key))
                 + ', Alice: ' + str(wallet.bch.money(keys['Alice'][1])) +
                 '. Len of bch: {}, of last block: {}'.format(str(len(wallet.bch)), str(len(wallet.bch[-1].txs)))
                 + '\n[{}, {}]'.format(str(len(wallet.bch)-1), str(len(wallet.bch[-1].txs)-1)))
        # 0 3
        wallet.bch.new_transaction(keys['Chuck'][1], [[0, 0]], [my_keys[1], keys['Chuck'][1]], [0.95, 0.05],
                                   'signing', keys['Chuck'][0])
        log.info('me: ' + str(wallet.bch.money(my_keys[1])) + ', you: ' + str(wallet.bch.money(your_pub_key))
                 + ', Alice: ' + str(wallet.bch.money(keys['Alice'][1])) +
                 '. Len of bch: {}, of last block: {}'.format(str(len(wallet.bch)), str(len(wallet.bch[-1].txs)))
                 + '\n[{}, {}]'.format(str(len(wallet.bch)-1), str(len(wallet.bch[-1].txs)-1)))
        # 0 4
        my_wallet.new_transaction(['sc[1, 0]'], [0.57])
        log.info('me: ' + str(wallet.bch.money(my_keys[1])) + ', you: ' + str(wallet.bch.money(your_pub_key))
                 + ', Alice: ' + str(wallet.bch.money(keys['Alice'][1])) +
                 '. Len of bch: {}, of last block: {}'.format(str(len(wallet.bch)), str(len(wallet.bch[-1].txs)))
                 + '\n[{}, {}]'.format(str(len(wallet.bch)-1), str(len(wallet.bch[-1].txs)-1)))
        # 0 5
        my_wallet.set_nick('meee')
        # 1 0, 1 1
        wallet.bch.append(mining.mine(wallet.bch))
        log.info('me: ' + str(wallet.bch.money(my_keys[1])) + ', you: ' + str(wallet.bch.money(your_pub_key))
                 + ', Alice: ' + str(wallet.bch.money(keys['Alice'][1])) +
                 '. Len of bch: {}, of last block: {}'.format(str(len(wallet.bch)), str(len(wallet.bch[-1].txs)))
                 + '\n[{}, {}]'.format(str(len(wallet.bch)-1), str(len(wallet.bch[-1].txs)-1)))
        # 1 2
        my_wallet.new_transaction([your_pub_key], [0.5])
        log.info('me: ' + str(wallet.bch.money(my_keys[1])) + ', you: ' + str(wallet.bch.money(your_pub_key))
                 + ', Alice: ' + str(wallet.bch.money(keys['Alice'][1])) +
                 '. Len of bch: {}, of last block: {}'.format(str(len(wallet.bch)), str(len(wallet.bch[-1].txs)))
                 + '\n[{}, {}]'.format(str(len(wallet.bch)-1), str(len(wallet.bch[-1].txs)-1)))
        # 1 3
        my_wallet.new_transaction(['meee'], [0.5])
        log.info('me: ' + str(wallet.bch.money(my_keys[1])) + ', you: ' + str(wallet.bch.money(your_pub_key))
                 + ', Alice: ' + str(wallet.bch.money(keys['Alice'][1])) +
                 '. Len of bch: {}, of last block: {}'.format(str(len(wallet.bch)), str(len(wallet.bch[-1].txs)))
                 + '\n[{}, {}]'.format(str(len(wallet.bch)-1), str(len(wallet.bch[-1].txs)-1)))
        with open('tests/scex.py', 'r') as f:
            wallet.bch.new_sc(f.readlines(), my_keys[1], my_keys[0], memsize=10000520)
        wallet.bch.commit()
        b = wallet.bch[1]
        #b.contracts[0].execute()
        #b.contracts[0].msgs.append(['sell', (my_keys[1], 0.05), str(list(cg.sign(json.dumps(['sell', (str(my_keys[1]), 0.05)]), my_keys[0]))), False])
        wallet.bch[1] = b
        #b.contracts[0].handle_messages()
        wallet.bch[1] = b
        #self.assertAlmostEqual(0.05, json.loads(b.contracts[0].memory.local)[0][my_keys[1]])
        print('validness checking started. Bch has now', len(wallet.bch), 'blocks, last block has', len(wallet.bch[-1].txs), 'txs.')
        v = wallet.bch.is_valid()
        self.assertTrue(v)
        b.contracts[0].memory.add('{}fads;"[]'*1000001)
        b.contracts[0].memory.peers = [my_keys[1], your_pub_key, '1', '2', '3', '4', '5', '6', '7', '8', '9']
        b.contracts[0].memory.distribute_peers()
        wallet.bch[1] = b
        self.assertEqual(len(b.contracts[0].memory.accepts), 3)
        self.assertTrue(b.contracts[0].is_valid(wallet.bch))
        # 2 0, 2 1
        wallet.bch.append(mining.mine(wallet.bch))
        log.info('me: ' + str(wallet.bch.money(my_keys[1])) + ', you: ' + str(wallet.bch.money(your_pub_key))
                 + ', Alice: ' + str(wallet.bch.money(keys['Alice'][1]))
                 + '\n[{}, {}]'.format(str(len(wallet.bch)-1), str(len(wallet.bch[-1].txs)-1)))
        # tests of SC tasks distribution and mining
        print('my money', wallet.bch.money(my_keys[1]))
        self.assertEqual(wallet.bch.money(my_keys[1]), 201.83)
        print('your money', wallet.bch.money(your_pub_key))
        self.assertEqual(wallet.bch.money(your_pub_key), 0.5)
        print('Passed!')


unittest.main()

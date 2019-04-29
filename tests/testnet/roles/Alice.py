"""
Alice is a honest user. Alice creates transactions and smart contracts.
Thread for sync must be started separately, wallet must be already created.
"""
import logging as log
from hodl.block.sc.memory import SCMemoryError
import time


def main(wallet, keys=None):
    log.info("Alice's main started")
    log.debug("Alice's money: " + str(wallet.bch.money(keys['Alice'][1])))
    log.debug(f'len(bch): {len(wallet.bch)}')
    # start blockchain checking thread
    # create transaction:
    ind = wallet.new_transaction([keys['Bob'][1]], [0.01])
    log.info('created transaction with index {}'.format(str(ind)))
    # create smart contract
    ind = wallet.new_sc('__answer__="hello, world!"')
    log.info('created sc with index {}'.format(ind))
    log.info(f"length of last block's sc_tasks: {len(wallet.bch[-1].sc_tasks)}")
    time.sleep(10)
    b = wallet.bch[ind[0]]
    log.info(f'distributing peers. len(peers): {len(b.txs[ind[1]].sc.memory.peers)}')
    while True:
        try:
            b.txs[ind[1]].sc.memory.distribute_peers()
            break
        except SCMemoryError:
            time.sleep(1)
    wallet.bch[ind[0]] = b
    # messages to smart contract
    # decentralized internet request

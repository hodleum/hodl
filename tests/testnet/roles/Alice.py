"""
Alice is a honest user. Alice creates transactions and smart contracts.
Thread for sync must be started separately, wallet must be already created.
"""
import block
import logging as log


def main(wallet, keys=None):
    log.info("Alice's main started")
    log.debug("Alice's money: " + str(wallet.bch.money(keys['Alice'][1])))
    # start blockchain checking thread
    # create transaction:
    ind = wallet.wallets[0].new_transaction([keys['Bob'][1]], [0.01])
    log.info('created transaction with index {}'.format(str(ind)))
    # create smart contract
    ind = wallet.wallets[0].new_sc('__answer__="hello, world!"')
    log.info('created sc with indicies {}'.format(ind))
    log.info(f"length of last block's sc_tasks: {len(wallet.bch[-1].sc_tasks)}")
    # messages to smart contract
    # decentralized internet request
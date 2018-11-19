"""
Dave isn't a honest user. Dave creates not valid transactions and smart contracts.
Thread for sync must be started separately, wallet must be already created.
"""
import block
import logging as log


def main(wallet, keys=None):
    log.info("Dave's main started")
    log.debug("Dave's money: " + str(wallet.bch.money(keys['Dave'][1])))
    # create not valid transaction
    # create transaction trying to steel Alice's money
    # create not valid smart contract
    # not valid messages to smart contract
    pass   # todo

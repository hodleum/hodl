"""
Bob is a honest user. Bob creates transactions and smart contracts, like Alice.
Thread for sync must be started separately, wallet must be already created.
"""
from hodl import block
import logging as log


def main(wallet, keys=None):
    log.info("Bob's main started")
    log.debug("Bob's money: " + str(wallet.bch.money(keys['Bob'][1])))
    # start blockchain checking thread
    # create transaction
    # create smart contract
    # messages to smart contract
    # decentralized internet request
    pass   # todo

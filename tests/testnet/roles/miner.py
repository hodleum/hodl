"""
This miner is just a honest miner.
Thread for sync must be started separately, wallet must be already created.
"""
import logging as log


def main(wallet, keys=None):
    log.info("miner's main started")
    log.debug("miner's money: " + str(wallet.bch.money(keys[1])))
    # start mining
    wallet.act()
    # wait
    input()

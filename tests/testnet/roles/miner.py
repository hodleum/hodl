"""
This miner is just a honest miner.
Thread for sync must be started separately, wallet must be already created.
"""
import block
import logging as log


def main(wallet, keys=None):
    log.info("miner's main started")
    log.debug("miner's money: " + str(wallet.bch.money(keys['miner'][1])))
    # start blockchain checking thread
    # start pow mining thread
    # start pok mining thread
    # wait
    pass   # todo

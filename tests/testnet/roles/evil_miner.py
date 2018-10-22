"""
This miner is an evil miner.
Thread for sync must be started separately, wallet must be already created.
"""
import block
import logging as log


def main(wallet, keys=None):
    log.info("evil_miner's main started")
    log.debug("evil_miner's money: " + str(wallet.bch.money(keys['evil_miner'][1])))
    # start pow mining thread, but don't calculate anything, just set any answer
    # start pok mining thread, but don't store anything, just set any answer
    # wait
    pass   # todo

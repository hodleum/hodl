"""
This miner is just a honest miner.
Thread for sync must be started separately, wallet must be already created.
"""
import block
from block.mining import sc_calculator
import logging as log
import time


def main(wallet, keys=None):
    log.info("miner's main started")
    log.debug("miner's money: " + str(wallet.bch.money(keys['miner'][1])))
    # start blockchain checking thread
    # start pow mining thread
    powminer = sc_calculator.PoWMiner(keys['miner'])
    log.info('PoWminer object created')
    log.info('task application_loop will be started just now')
    powminer.task_application_loop(wallet.bch)
    powminer.run_tasks(wallet.bch)
    # start pok mining thread
    # wait
    pass   # todo

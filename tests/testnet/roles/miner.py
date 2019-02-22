"""
This miner is just a honest miner.
Thread for sync must be started separately, wallet must be already created.
"""
from hodl.block.mining import sc_calculator, sc_memory_miner
import logging as log
import time


def main(wallet, keys=None):
    log.info("miner's main started")
    log.debug("miner's money: " + str(wallet.bch.money(keys[1])))
    # todo: start blockchain checking thread
    # start pok mining thread
    pokminer = sc_memory_miner.PoKMiner(keys[1], keys[0])
    pokminer.main_thread(wallet.bch)
    # start pow mining thread
    powminer = sc_calculator.PoWMiner(keys[1], keys[0])
    log.info('task application_loop will be started just now')
    powminer.task_application_loop(wallet.bch)
    # run pow task
    powminer.run_tasks(wallet.bch)
    # wait

"""
This miner is just a honest miner.
Thread for sync must be started separately, wallet must be already created.
TODO: PoK mining test
"""
from hodl import block
from hodl.block.mining import sc_calculator, sc_memory_miner
import logging as log
import time


def main(wallet, keys=None):
    log.info("miner's main started")
    log.debug("miner's money: " + str(wallet.bch.money(keys['miner'][1])))
    # start blockchain checking thread
    # start pow mining thread
    powminer = sc_calculator.PoWMiner(keys['miner'][1], keys['miner'][0])
    time.sleep(5.5)
    log.info('task application_loop will be started just now')
    powminer.task_application_loop(wallet.bch)
    powminer.run_tasks(wallet.bch)
    # start pok mining thread
    pokminer = sc_memory_miner.PoKMiner(keys['miner'][1], keys['miner'][0])
    pokminer.mining_thread(wallet.bch)
    # wait
    pass   # todo

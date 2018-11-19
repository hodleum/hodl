"""
Bob is a honest passive user.
Thread for sync must be started separately, wallet must be already created.
"""
import block
import logging as log


def main(wallet, keys=None):
    log.info("Chuck's main started")
    log.debug("Chuck's money: " + str(wallet.bch.money(keys['Chuck'][1])))
    # start blockchain checking thread
    pass   # todo

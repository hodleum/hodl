"""
Alice is a honest user. Alice creates transactions and smart contracts.
Thread for sync must be started separately, wallet must be already created.
"""
import block


def main(wallet, keys=None):
    # start blockchain checking thread
    # create transaction:
    wallet.wallets[0].new_transaction([keys['Bob'][1]], [0.01])
    # create smart contract
    # messages to smart contract
    # decentralized internet request
    pass   # todo

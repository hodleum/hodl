from .daemon import app
import json
from hodl.block.Blockchain import Blockchain


bch = Blockchain()


@app.route('/get_block/<int:blck>')
def get_block(blck):
    """
    Get a block from blockchain
    :param blck: index of block to get
    :type blck: int
    :return: block's string representation
    :rtype: str
    """
    return str(bch[blck])


@app.route('/get_sc/<string:scind>')
def get_sc(scind):
    """
    Get smart contract (str) by index
    :param scind: sc index, e.g. 'sc[a, b]' or '[a, b]'
    :type scind: str
    :return:
    """
    return str(bch.get_sc(scind))


@app.route('/get_tnx/<string:tnx>')
def get_tnx(tnx):
    """
    Get transaction (its string representation) by index
    :param tnx: index
    :type tnx: str
    :return: transaction (str)
    :rtype: str
    """
    return str(bch[json.loads(tnx)])

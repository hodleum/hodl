"""
Sync algorythm:
Alice(A) sends len(A.bch), len(A.bch[-1].txs), len(A.bch[-1].contracts) and A.bch[-2].h
Bob(b) sends len(B.bch), len(B.bch[-1].txs), len(B.bch[-1].contracts), if len(B.bch) < len(A.bch) B sends request of blocks,
    if len(B.bch)==len(A.bch):
        if B.bch[-2].h == A.bch[-2].h:
            Bob sends request if his lists of txs or contracts in bch[-1] are shorter
        else:
            Bob sends his hashes for last 500 blocks
                and they decide where their chains are not equal    todo
If Alice's blockchain is shorter, A sends request,
if len(A.bch) == len(B.bch), if lengths of Alice's lists of bch[-1]'s txs or contracts are shorter, A sends request
"""
import logging as log
from hodl import block
# todo: fix import problem here
import hodl.net.protocol.server as server
import hodl.net.models.Message as Message
import hodl.net.server.protocol as protocol
import hodl.net.server.user as user


bch = block.Blockchain()
syncs = []
keys = []


class SyncHandler:
    """
    Class for synchronization conversation with one peer
    """
    def __init__(self, address, msg=None, u=None):
        """
        :param address: peer address
        :param msg: start message
        :param u: peer object to send messages to
        """
        self.address = address
        self.msgs = []
        # todo: realize algorythm above
        if not msg:
            answer = dict()
            u.send(Message('sync', answer))
        else:
            u.send(self.on_message(msg))

    def on_message(self, msg):
        answer = dict()
        self.msgs.append(msg)
        # todo: getting object from other peers
        # todo: realize algorythm above
        # todo: if synchronization complete, delete history
        return answer


@server.handle('sync')
def handle_msg(msg):
    """
    Handle sync message
    :param msg: message
    :type msg: str
    """
    log.debug('new sync message')
    h = {u.address: u for u in syncs}.get(user.public_key)
    # if we have sync history with this user, use it
    if h:
        user.send(Message('sync', h.on_message(msg)))
    # if we receive message from this user at first time, create conversation
    else:
        log.debug('new sync conversation with ' + str(user.name))
        h = SyncHandler(user.public_key, msg, user)
        user.send(Message('sync', h.on_message(msg)))
        syncs.append(h)


@server.handle('sc_mem_get')
def handle_mem_get_request(msg):
    pass   # todo


def loop(my_keys):
    log.debug('sync loop')
    keys = my_keys
    server.run()

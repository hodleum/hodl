"""
Sync algorythm:
Alice(A) sends len(A.bch), len(A.bch[-1].txs), len(A.bch[-1].contracts) and A.bch[-2].h
Bob(b) sends len(B.bch), len(B.bch[-1].txs), len(B.bch[-1].contracts), if len(B.bch) < len(A.bch) B sends request of blocks,
    if len(B.bch)==len(A.bch):
        if B.bch[-2].h == A.bch[-2].h:
            Bob sends request if his lists of txs or contracts in bch[-1] are shorter
        else:
            Bob sends his hashes for last 500 blocks
                and they decide where their chains are not equal    # todo
If Alice's blockchain is shorter, A sends request,
if len(A.bch) == len(B.bch), if lengths of Alice's lists of bch[-1]'s txs or contracts are shorter, A sends request
"""
import block
import net


bch = block.Blockchain()


class SyncHandler:
    def __init__(self, address, msg=None):
        self.address = address
        self.msgs = []
        # todo
        if not msg:
            answer = dict()
            net.send_to(address, answer)
        else:
            self.on_message(msg)

    def on_message(self, msg):
        answer = []
        self.msgs.append(msg)
        # todo
        return answer

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

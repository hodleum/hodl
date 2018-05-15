import json
import time
import cryptogr as cg
from block.Smart_contract import Smart_contract


allowed_imports = []


def is_allowed_import(c):
    v = False
    for i in allowed_imports:
        if c.startswith(i) and c[len(i)] == '\n':
            v = True
    return v


class SimpleSC(Smart_contract):
    """SC which executes by exec."""
    def __init__(self, *args):
        super().__init__(*args)

    def check(self):
        if 'exec' in self.code or 'eval' in self.code or 'open' in self.code:
            return False
        if 'import ' not in self.code:
            return True
        else:
            for i in range(len(self.code)):
                if self.code[i:i+6] == 'import':
                    if not is_allowed_import(self.code[i+6:]):
                        return False
        return True

    def execute(self):
        exec(self.code)

    def is_valid(self, bch):
        return self.check() and super().is_valid(bch)
